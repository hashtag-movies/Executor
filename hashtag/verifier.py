import re


class HashtagVerifier:
    def verify(self, plan, execution):
        errors = []
        warnings = []

        plan = plan or {}
        execution = execution or {}

        text = str(execution.get("text", "") or "")
        before = str(execution.get("inputText", "") or "")

        # ------------------------------------------------------------
        # BODY EXECUTION STATUS
        #
        # A Body operation is only successful when the Body explicitly
        # reports status == "success".
        #
        # permission_required, denied, error, etc. are NOT success.
        # ------------------------------------------------------------

        execution_status = str(
            execution.get("status", "") or ""
        ).strip().lower()

        if execution_status and execution_status != "success":
            body_error = (
                execution.get("error")
                or execution.get("message")
                or f"Body execution status: {execution_status}"
            )

            if execution_status == "permission_required":
                errors.append(
                    f"Body permission is required before execution can "
                    f"be verified: {body_error}"
                )

            elif execution_status in {
                "denied",
                "permission_denied",
            }:
                errors.append(
                    f"Body execution was denied: {body_error}"
                )

            else:
                errors.append(
                    f"Body execution failed: {body_error}"
                )

        # ------------------------------------------------------------
        # EXISTING V10 VERIFICATION
        # ------------------------------------------------------------

        for action in plan.get("actions", []):
            cap = action.get("capability") or action.get("operation")
            args = action.get("arguments") or {}

            if cap == "text.remove_digits":
                if re.search(r"\d", text):
                    errors.append(
                        "Digits remain after remove_digits."
                    )

            elif cap == "text.remove_letters":
                if re.search(r"[A-Za-z]", text):
                    errors.append(
                        "Letters remain after remove_letters."
                    )

            elif cap == "text.replace":
                old = str(args.get("old", ""))

                if old and old in text:
                    errors.append(
                        f"Requested text {old!r} still exists."
                    )

                elif old and old.casefold() in text.casefold():
                    errors.append(
                        f"Requested text {old!r} still exists "
                        "with different capitalization."
                    )

            elif cap == "format.pick_fields":
                fields = list(args.get("fields") or [])
                delimiter = str(
                    args.get("delimiter", ":")
                )

                for line in text.splitlines():
                    if (
                        line
                        and len(line.split(delimiter))
                        != len(fields)
                    ):
                        errors.append(
                            "Field projection produced an unexpected "
                            "field count."
                        )
                        break

            elif cap == "format.lowercase":
                if text != text.lower():
                    errors.append(
                        "Output is not fully lowercase."
                    )

            elif cap == "format.uppercase":
                if text != text.upper():
                    errors.append(
                        "Output is not fully uppercase."
                    )

            elif cap == "format.remove_duplicates":
                lines = [
                    line
                    for line in text.splitlines()
                    if line.strip()
                ]

                if len(lines) != len(set(lines)):
                    errors.append(
                        "Duplicate output lines remain."
                    )

        # ------------------------------------------------------------
        # EXISTING APPLICABILITY WARNING
        # ------------------------------------------------------------

        if (
            before
            and text == before
            and plan.get("actions")
            and execution_status in {"", "success"}
        ):
            warnings.append(
                "Execution returned text identical to input; "
                "verify applicability."
            )

        return {
            "ok": not errors,
            "errors": errors,
            "warnings": warnings,
            "replan": bool(errors),
        }