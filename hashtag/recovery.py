import re

class RecoveryEngine:
    """Choose a bounded, deterministic alternative when verification fails."""
    MAX_REPLANS = 2

    def replan(self, plan, verification, input_text, output_text):
        errors = verification.get("errors") or []
        actions = plan.get("actions") or []
        # Recovery 1: case mismatch for literal removal/replacement.
        if any(a.get("capability") == "text.replace" for a in actions):
            for a in actions:
                if a.get("capability") != "text.replace":
                    continue
                args = a.get("arguments") or {}
                old = str(args.get("old", ""))
                new = str(args.get("new", ""))
                if not old or old.casefold() not in (input_text or "").casefold() or old.casefold() not in (output_text or "").casefold():
                    continue
                variants = {m.group(0) for m in re.finditer(re.escape(old), input_text or "", re.I)}
                if variants and any(v != old for v in variants):
                    return {
                        "actions": [{
                            "capability": "text.regex_replace",
                            "arguments": {"pattern": re.escape(old), "to": new, "flags": "gi"},
                            "reason": f"Recovery: the requested text was present with different capitalization; retry case-insensitively.",
                            "source": "recovery"
                        }],
                        "reason": "Case-insensitive retry generated after verification detected that the requested literal did not match the input casing."
                    }
        # Recovery 2: if output did not change and a literal replacement target exists,
        # retry with regex escaping so literal punctuation cannot be interpreted oddly.
        if any("did not change" in str(e).lower() for e in errors):
            for a in actions:
                if a.get("capability") == "text.replace":
                    args=a.get("arguments") or {}; old=str(args.get("old", "")); new=str(args.get("new", ""))
                    if old and old in (input_text or ""):
                        return {
                            "actions": [{"capability":"text.regex_replace","arguments":{"pattern":re.escape(old),"to":new,"flags":"g"},"reason":"Recovery: retry the same literal operation as a safe regex replacement.","source":"recovery"}],
                            "reason":"Literal replacement did not change the output even though the target was present; retrying with an escaped regex."
                        }
        return None
