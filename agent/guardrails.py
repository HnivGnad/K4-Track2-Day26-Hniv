"""Pure answer checks: grounding, injection patterns, redaction and numeric support.

Answers bypass Gateway.decide in the kit. Call review_answer when assembling an
answer; prompt.md carries the same requirements for the model's ANSWER action.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

# kit.world.anchor is a collaborator's file (workspace hard rule 2). Present
# and stable as of this writing; degraded gracefully so `check_grounding`
# still runs (with the anchor-syntax leg of the check skipped, not silently
# treated as passing) if it is ever briefly unimportable.
try:
    from kit.world.anchor import Anchor, AnchorSyntaxError
    _ANCHOR_AVAILABLE = True
except ImportError:  # pragma: no cover - collaborator file
    Anchor = None  # type: ignore[assignment]
    AnchorSyntaxError = ValueError  # type: ignore[assignment, misc]
    _ANCHOR_AVAILABLE = False

__all__ = [
    "GroundingResult",
    "check_grounding",
    "InjectionScanResult",
    "scan_for_injected_instructions",
    "RedactionResult",
    "redact",
    "ArithmeticCheckResult",
    "verify_arithmetic",
    "abstention_policy",
]


# ---------------------------------------------------------------------------
# 1. GROUNDING — real, working.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GroundingResult:
    grounded: bool
    cited: tuple[str, ...]
    ungrounded: tuple[str, ...]  # cited, syntactically valid, but never retrieved this exchange
    malformed: tuple[str, ...]  # cited but not even valid Anchor syntax


def check_grounding(
    answer: Mapping[str, Any],
    retrieved_anchors: Iterable[str],
    *,
    require_citation: bool = True,
) -> GroundingResult:
    """"Every claim traces to a returned anchor" (this task's own brief),
    made concrete: every string in `answer["cited_anchors"]` must (a) parse
    as valid `ns:slug[/rev][/idx][#span]` syntax (`kit.world.anchor.Anchor`)
    and (b) be a member of `retrieved_anchors` — the anchors YOUR exchange
    actually got back from a `tool_result` this round, not anchors you
    recognise from having seen them before, and not anchors you are
    inferring exist.

    `retrieved_anchors` is YOUR responsibility to assemble honestly — the
    right source is the union of every `tool_result.anchors` your agent
    received this exchange (CONTRACTS.md 5.2's `tool_result` event field),
    never something wider like "every anchor this world index contains".
    Passing a wider set than what you actually retrieved makes this
    function agree with citations that are `ungrounded` in the sense that
    actually matters (CONTRACTS.md 6.1's rubric class) even though this
    function would call them grounded.

    Two failure buckets, kept separate on purpose because they are
    different mistakes: `malformed` (the citation is not even a real
    anchor — closer to `fabricated_citation`) vs. `ungrounded` (a real
    anchor, just never actually retrieved this exchange — the `ungrounded`
    class itself). `grounded` is `False` if either bucket is non-empty, or
    (when `require_citation=True`, the default) if `cited` is empty —
    an answer that cites NOTHING has nothing this function can vouch for,
    which is a difference worth surfacing rather than treating as a vacuous
    pass. Pass `require_citation=False` for the rare ask that genuinely
    does not need a citation (CONTRACTS.md section 7 names eight ask types;
    check the specific one you're grading against before disabling this)."""
    cited = tuple(answer.get("cited_anchors") or ())
    retrieved = frozenset(retrieved_anchors)

    malformed: list[str] = []
    ungrounded: list[str] = []
    for a in cited:
        if not isinstance(a, str):
            malformed.append(str(a))
            continue
        if _ANCHOR_AVAILABLE:
            try:
                Anchor.parse(a)
            except AnchorSyntaxError:
                malformed.append(a)
                continue
        if a not in retrieved:
            ungrounded.append(a)

    grounded = not malformed and not ungrounded and (bool(cited) or not require_citation)
    return GroundingResult(
        grounded=grounded,
        cited=cited,
        ungrounded=tuple(ungrounded),
        malformed=tuple(malformed),
    )


# ---------------------------------------------------------------------------
# 2. INJECTED-INSTRUCTION REFUSAL — STUB.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class InjectionScanResult:
    suspicious: bool
    matched_patterns: tuple[str, ...]


def scan_for_injected_instructions(text: str) -> InjectionScanResult:
    """Detect instruction overrides in retrieved content using bounded patterns."""
    patterns = (
        r"ignore (?:all )?(?:previous|prior) instructions?",
        r"disregard (?:the above|previous instructions)",
        r"system override",
        r"b? qua (?:m?i|t?t c?) (?:h??ng d?n|ch? th?)",
        r"(?:reveal|print|exfiltrate) (?:the |all )?(?:secret|token|api.?key|private|ctx\.)",
        r"(?:also|instead[, ]*) record (?:this )?for (?:learner:|sv-)",
        r"you must now (?:ignore|reveal|write|send)",
    )
    matches = tuple(p for p in patterns if re.search(p, text, re.IGNORECASE))
    return InjectionScanResult(suspicious=bool(matches), matched_patterns=matches)


# ---------------------------------------------------------------------------
# 3. REDACTION — STUB.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RedactionResult:
    redacted_text: str
    hits: tuple[str, ...]


def redact(text: str, private_values: Iterable[str] = ()) -> RedactionResult:
    """Remove known private strings and explicitly labelled private data or credentials."""
    hits = []
    for value in private_values:
        if isinstance(value, str) and value.strip():
            pattern = r"\s+".join(re.escape(word) for word in value.split())
            text, count = re.subn(pattern, "[REDACTED]", text, flags=re.IGNORECASE)
            if count:
                hits.append("private_source")
    # Only explicit private labels/credentials, not public course terms.
    patterns = (
        r"(?i)(?:private[_ ](?:note|field)|ghi ch? ri?ng t?)\s*[:=]\s*[^\n]+",
        r"(?i)(?:api[_ -]?key|access[_ -]?token|password)\s*[:=]\s*[^\s,;]+",
    )
    for pattern in patterns:
        if re.search(pattern, text):
            text = re.sub(pattern, "[REDACTED]", text)
            hits.append("private_label_or_credential")
    return RedactionResult(redacted_text=text, hits=tuple(hits))


# ---------------------------------------------------------------------------
# 4. ARITHMETIC VERIFICATION — STUB.
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ArithmeticCheckResult:
    checked: bool
    ok: bool | None
    detail: str


_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def verify_arithmetic(text: str, source_text: str | None = None) -> ArithmeticCheckResult:
    """Compare numeric literals with sources; no source means unverified, not approved."""
    numbers = _NUMBER_RE.findall(text)
    if not numbers:
        return ArithmeticCheckResult(True, True, "No numeric assertions")
    if source_text is None:
        return ArithmeticCheckResult(False, None, "Numeric assertions need retrieved source text")
    supported = set(_NUMBER_RE.findall(source_text))
    missing = [n for n in numbers if n not in supported]
    return ArithmeticCheckResult(True, not missing,
                                 "Unsupported numeric literals: " + ", ".join(missing)
                                 if missing else "Numeric literals match retrieved sources")


# ---------------------------------------------------------------------------
# 5. ABSTENTION POLICY — real, naive.
# ---------------------------------------------------------------------------


def abstention_policy(grounding: GroundingResult) -> bool:
    """Abstain when grounding fails; use review_answer for full required-field and privacy checks."""
    return not grounding.grounded
