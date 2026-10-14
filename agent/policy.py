"""Pure gateway policy. Trust only arena context and signed admission data."""
from __future__ import annotations

import json
from kit.mcp.a2a import SKILL_ROUTES, verify_card, verify_delegation
from kit.mcp.specs import A2A_PEERS, TOOL_SPECS
from kit.mcp.servers import _LOCAL_TOOL_SPECS
from agent.guardrails import scan_for_injected_instructions
from agent.strategy import successor_of


def learner_id(value):
    return str(value or "").removeprefix("Learner:").removeprefix("learner:")


class Policy:
    def __init__(self, ctx):
        self.ctx = ctx
        self.cards = {}
        self.etags = {}
        self.tokens = set()
        self.writes = set()
        self.idempotency = set()
        self.rates = {}
        self.spent = {}

    def note_card(self, server, card):
        # A bare `verified` flag is supplied by the LOCAL spar harness, not a
        # signature. It must never grant admission in a tournament.
        result = verify_card(card)
        if result.admitted and result.peer == server:
            self.cards[server] = result.declared_skills
        else:
            self.cards.pop(server, None)

    def note_provenance(self, anchor, etag):
        if isinstance(anchor, str) and isinstance(etag, str) and etag:
            self.etags[anchor] = (etag, self.ctx.round, self.ctx.call_index)

    def prepare(self, cmd):
        """Return (call arguments, error). No execution and no external reads."""
        server, tool = successor_of(cmd.server, cmd.tool) or (cmd.server, cmd.tool)
        spec = TOOL_SPECS.get((server, tool)) or _LOCAL_TOOL_SPECS.get((server, tool))
        if spec is None:
            return None, "unknown tool; select a declared tool"
        if (server in A2A_PEERS) != (cmd.kind == "a2a"):
            return None, "command transport does not match server type"
        args = dict(cmd.args)
        headers = {str(k).lower(): v for k, v in cmd.headers.items()}
        if any(args.get(k) for k in ("route", "_route", "replica")):
            return None, "replica routing must use headers"
        if headers.get("x-server-fingerprint") == "unvouched" or headers.get("x-card-signature") == "invalid":
            return None, "untrusted server identity or card signature"
        if args.get("peer_unverified"):
            return None, "peer answer requires independent source verification"
        for key in ("learner", "learner_id", "subject"):
            if args.get(key) and learner_id(args[key]) != learner_id(self.ctx.act):
                return None, "target learner differs from act"
        target = args.get("target")
        if target and str(target).lower().startswith("learner:") and learner_id(target) != learner_id(self.ctx.act):
            return None, "target learner differs from act"
        if scan_for_injected_instructions(" ".join(str(v) for v in args.values())).suspicious:
            return None, "instruction embedded in source data"
        if len(str(args.get("catalog", ""))) > 1024:
            return None, "catalog payload exceeds bounded discovery"

        scopes = set(self.ctx.scopes)
        needed_scope = f"wiki.write:{server}" if spec.is_write else "wiki.read"
        if needed_scope not in scopes:
            return None, f"missing scope {needed_scope}"
        token_id = None
        if server in A2A_PEERS:
            skills = self.cards.get(server, ())
            if not any(skill == tool or SKILL_ROUTES.get(skill) == (server, tool) for skill in skills):
                return None, "peer card not verified or skill not declared"
            if headers.get("aud") not in (server, f"a2a:{server}"):
                return None, "delegation audience differs from peer"
            token = args.get("delegation") or headers.get("delegation")
            if isinstance(token, str):
                try:
                    token = json.loads(token)
                except (ValueError, TypeError):
                    token = None
            if not isinstance(token, dict):
                return None, "signed per-hop delegation required"
            result = verify_delegation(token, aud=f"a2a:{server}",
                                       call_index=cmd.call_index, expected_act=self.ctx.act,
                                       seen_token_ids=self.tokens)
            if not result.admitted:
                return None, "delegation failed signature, ownership, expiry or replay check"
            token_id = token["token_id"]

        if spec.needs_lease and (not cmd.lease_id or cmd.lease_id not in self.ctx.leases):
            return None, "get_frame requires a live query lease"
        replica = headers.get("mcp-replica", "w")
        if replica not in ("w", "c"):
            return None, "invalid replica header"
        headers["mcp-replica"] = replica
        fields = cmd.fields
        if not fields or fields == ("*",):
            if (server, tool) == ("registry", "list_servers"):
                fields = ("name",)
            elif (server, tool) == ("glossary", "list_terms"):
                fields = ("term",)
            else:
                fields = spec.default_fields
        if any(f not in spec.all_fields for f in fields):
            return None, "field mask contains unsupported fields"

        write_key = None
        if spec.is_write:
            anchor = str(args.get("anchor") or args.get("learner") or "")
            pin = self.etags.get(anchor)
            if not pin or pin[1] != self.ctx.round or not 0 <= cmd.call_index - pin[2] <= 3:
                return None, "write requires fresh provenance for its target"
            if headers.get("if-match") != pin[0] or not headers.get("idempotency-key"):
                return None, "write requires matching If-Match and Idempotency-Key"
            write_key = (server, tool, anchor, json.dumps(args, sort_keys=True))
            if write_key in self.writes:
                return None, "write already authorized; reconcile its receipt before retrying"
            if headers["idempotency-key"] in self.idempotency:
                return None, "idempotency key already used by an authorized write"

        rnd = self.ctx.round
        if spec.rate_limit:
            limit, window = spec.rate_limit
            recent = [r for r in self.rates.get((server, tool), []) if rnd - window < r <= rnd]
            if len(recent) >= limit:
                return None, "tool rate window exhausted"
        # Bound row-priced queries; a partial page requires continuation rather
        # than an assumption that omitted matches do not exist.
        rows = 1
        if (server, tool) == ("slides", "query"):
            try:
                requested = int(args.get("limit", 2))
            except (TypeError, ValueError):
                return None, "query limit must be an integer"
            if requested < 1:
                return None, "query limit must be positive"
            rows = min(requested, 3)
            args["limit"] = rows
        estimate = spec.base + sum(spec.field_weight[f] for f in fields) + rows * spec.row_weight
        reserve = max(0, 10 - rnd) * 7
        if estimate > self.ctx.credits or self.ctx.credits - estimate < reserve:
            return None, "call would consume credits reserved for later rounds"
        if self.spent.get(rnd, 0) + estimate > 11:
            return None, "round credit allowance exhausted"
        self.spent[rnd] = self.spent.get(rnd, 0) + estimate
        self.rates.setdefault((server, tool), []).append(rnd)
        if token_id:
            self.tokens.add(token_id)
        if write_key:
            self.writes.add(write_key)
            self.idempotency.add(headers["idempotency-key"])
        return dict(server=server, tool=tool, args=args, fields=tuple(fields),
                    headers=headers, lease_id=cmd.lease_id, call_index=cmd.call_index), None
