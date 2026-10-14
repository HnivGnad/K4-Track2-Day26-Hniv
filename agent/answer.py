"""Validate assembled answers against this exchange's actual observations."""
from agent.guardrails import check_grounding, redact, verify_arithmetic


def review_answer(answer, ask, results):
    """Return (safe answer, issues). Caller publishes only when issues is empty.

    Pure helper; the kit's loop does not expose an answer interception hook,
    so prompt.md also requires these checks before ANSWER.
    """
    successful = [r for r in results if r.get("ok") is True]
    retrieved = {a for r in successful for a in r.get("anchors", [])}
    private = [str(row.get("body", "")) for r in successful
               for row in r.get("rows", []) if row.get("private") is True]
    issues = []
    if not check_grounding(answer, retrieved).grounded:
        issues.append("citations missing, malformed or not retrieved this exchange")
    for field in ask.get("require", []):
        if field not in answer or answer[field] is None:
            issues.append(f"missing required field: {field}")
    cited = set(answer.get("cited_anchors", []))
    if any(r.get("partial") and cited.intersection(r.get("anchors", [])) for r in successful):
        # Scope questions that need complete coverage require explicit exhaustion.
        if ask.get("type") in ("which_day_covers", "whatlinkshere", "contradiction_between"):
            cursors = {str(r.get("continuation")) for r in successful if r.get("partial")}
            consumed = {str(r.get("request_cursor")) for r in successful if "request_cursor" in r}
            if not cursors <= consumed:
                issues.append("partial result has unfetched continuation")
    privacy_hits = []

    def clean(value):
        if isinstance(value, str):
            redaction = redact(value, private)
            privacy_hits.extend(redaction.hits)
            return redaction.redacted_text
        if isinstance(value, dict):
            return {k: clean(v) for k, v in value.items()}
        if isinstance(value, list):
            return [clean(v) for v in value]
        return value

    safe = clean(answer)
    if privacy_hits:
        issues.append("private data removed; rebuild public answer")
    source = " ".join(str(v) for r in successful for row in r.get("rows", [])
                      for v in row.values() if isinstance(v, (str, int, float)))
    numeric_text = safe["text"]
    for anchor in cited:
        numeric_text = numeric_text.replace(anchor, "")
    numeric = verify_arithmetic(numeric_text, source)
    if numeric.ok is False:
        issues.append(numeric.detail)
    return safe, tuple(issues)
