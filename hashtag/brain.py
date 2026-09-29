import re
from collections import Counter
from .contracts import Action, Operation

FIELD_ALIASES = {
    "user": "username", "usr": "username", "login": "username", "username": "username",
    "pass": "password", "pwd": "password", "password": "password",
    "mail": "email", "email": "email", "e-mail": "email",
    "name": "name", "fullname": "name", "full_name": "name",
    "phone": "phone", "mobile": "phone", "tel": "phone",
    "url": "url", "link": "url", "token": "token", "key": "token", "secret": "secret",
}


class DataInspector:
    def inspect(self, text):
        text = text or ""
        lines = text.splitlines()
        nonempty = [x for x in lines if x.strip()]
        separators = Counter()
        samples = []
        for line in nonempty[:1000]:
            for sep in (":", "|", "->", "=>", ",", "\t", ";", "="):
                if sep in line:
                    separators[sep] += 1
            samples.append(self._split_best(line))
        delimiter = separators.most_common(1)[0][0] if separators else ""
        counts = Counter(len(x) for x in samples)
        field_count = counts.most_common(1)[0][0] if counts else 0
        first_fields = []
        for i in range(min(field_count, 12)):
            vals = [row[i].strip() for row in samples if len(row) > i and row[i].strip()]
            first_fields.append({"position": i + 1, "samples": vals[:5]})
        return {
            "lineCount": len(lines),
            "nonEmptyLines": len(nonempty),
            "hasDigits": bool(re.search(r"\d", text)),
            "digitCount": len(re.findall(r"\d", text)),
            "letterCount": len(re.findall(r"[A-Za-z]", text)),
            "numberOnlyLines": sum(bool(re.fullmatch(r"\s*\d+(?:\.\d+)?\s*", x)) for x in lines),
            "separators": [s for s, _ in separators.most_common(7)],
            "delimiter": delimiter,
            "fieldCount": field_count,
            "firstFields": first_fields,
            "sample": lines[:8],
            "wordSample": re.findall(r"[A-Za-z_][A-Za-z0-9_]*", text)[:20],
        }

    @staticmethod
    def _split_best(line):
        candidates = [":", "|", "->", "=>", ",", "\t", ";", "="]
        present = [(line.count(s), s) for s in candidates if s in line]
        return line.split(max(present)[1]) if present else [line]


class HashtagBrain:
    VERSION = "10.0.0"

    def __init__(self, memory=None, learner=None, provider=None):
        self.inspector = DataInspector()
        self.memory = memory
        self.learner = learner
        self.provider = provider

    def plan(self, tool, request, context=None):
        context = context or {}
        text = (request or "").strip()
        low = text.lower()
        caps = self._capability_ids(tool)
        sample = str(context.get("inputText", "") or "")
        inspection = self.inspector.inspect(sample) if sample else None
        actions = []

        def add(cap, args=None, reason="", source="brain"):
            args = args or {}
            if cap not in caps:
                return False
            if not self._valid_action_arguments(cap, args):
                return False
            if not any(a["capability"] == cap and a["arguments"] == args for a in actions):
                actions.append(Action(cap, args, reason, source).as_dict())
            return True

        if self.learner:
            for a in self.learner.reuse(tool.get("id"), text, tool.get("capabilities", [])):
                add(a["capability"], a.get("arguments", {}), a.get("reason", "Reused learned skill."), "learned")

        # Existing V10 text/format intelligence remains authoritative.
        if self._asks_remove_digits(low):
            add("text.remove_digits", {}, "Remove every numeric character (0-9) from the input.")
        if self._asks_remove_letters(low):
            add("text.remove_letters", {}, "Remove alphabetic characters from every line.")
        target = self._generic_remove_target(text)
        if target and not self._asks_remove_digits(low) and not self._asks_remove_letters(low):
            add("text.replace", {"old": target, "new": ""}, f"Remove the requested text {target!r}.")

        m = re.search(
            r'(?:replace|change)\s+(?:the\s+)?(?:text\s+)?["â€œ\']?(.+?)["â€\']?\s+(?:with|to|into)\s+["â€œ\']?(.+?)["â€\']?(?:\s*$|[.!?]$)',
            text,
            re.I,
        )
        if m:
            old = m.group(1).strip().strip('"â€œâ€\'')
            new = m.group(2).strip().strip('"â€œâ€\'')
            if old and new:
                add("text.replace", {"old": old, "new": new}, f"Replace {old!r} with {new!r}.")

        if self._asks_remove_duplicates(low):
            add("format.remove_duplicates", {}, "Remove duplicate lines.")
        if self._asks_remove_number_only(low):
            add("format.remove_number_only", {}, "Remove lines containing only numbers.")
        sep = self._separator(text)
        if sep and any(x in low for x in ("before", "left side", "left of", "remove everything after")):
            add("format.keep_before", {"separator": sep}, f"Keep the text before {sep!r}.")
        if sep and any(x in low for x in ("keep after", "take after", "text after", "right side", "right of", "remove everything before")):
            add("format.keep_after", {"separator": sep}, f"Keep the text after {sep!r}.")
        if self._asks_lower(low):
            add("format.lowercase", {}, "Convert output to lowercase.")
        if self._asks_upper(low):
            add("format.uppercase", {}, "Convert output to uppercase.")
        field_action = self._infer_field_projection(text, inspection)
        if field_action:
            add(field_action["capability"], field_action["arguments"], field_action["reason"])

        m = re.search(r'\b(?:join|combine|merge)\s+(?:every|each)\s+(\d+)\s+lines?(?:.*?)(?:with|using|by)\s+(colon|comma|semicolon|pipe|tab|space|[,:;|])', low)
        if m:
            add("format.join_blocks", {"size": int(m.group(1)), "delimiter": self._delimiter(m.group(2))}, "Join each requested line block.")
        if any(x in low for x in ("sort lines", "sort the lines", "alphabetically", "alphabetical order")):
            add("format.sort_lines", {"order": "desc" if any(x in low for x in ("descending", "z to a", "reverse order")) else "asc"}, "Sort lines.")
        m = re.search(r'regex\s+(?:replace|remove)\s+["\'](.+?)["\'](?:\s+(?:with|to)\s+["\'](.*?)["\'])?$', text, re.I)
        if m:
            add("text.regex_replace", {"pattern": m.group(1), "to": m.group(2) or "", "flags": "g"}, "Use the requested regex.")

        # Semantic model gets the first chance to interpret a natural-language
        # request when a provider is configured. This is intentionally before
        # legacy body-specific phrase inference so deterministic aliases cannot
        # incorrectly claim an ambiguous request (for example, treating a file
        # path mentioned with the word "inside" as a directory-list request).
        # The provider remains advisory: only advertised capabilities are
        # accepted, and the existing execution/permission pipeline remains
        # authoritative.
        # Resolve an explicit folder-listing request before semantic-provider
        # invocation. This preserves the established deterministic capability
        # path while still allowing the provider to handle genuinely ambiguous
        # requests such as a file containing the word "inside".
        folder_path = self._extract_path(text, context)
        folder_request = self._asks_folder_contents(low, path_hint=folder_path)
        if folder_request and folder_path and "filesystem.list" in caps:
            add(
                "filesystem.list",
                {"path": folder_path},
                f"Mapped the request for the folder contents to filesystem.list using {folder_path!r}.",
            )

        provider_used = False
        provider_goal_complete = False
        provider_attempted = False
        provider_error = None
        provider_returned = False

        # A continuation turn already has physical execution evidence from the
        # previous step. In that situation the semantic provider is authoritative
        # for the next goal-directed operation. If it fails, do not silently
        # fall back to generic body-capability inference.
        continuation = bool(
            context.get("last_operation")
            or context.get("observations")
            or context.get("completed_operations")
        )

        provider_available = False
        if self.provider is not None:
            try:
                availability = getattr(self.provider, "available", None)
                provider_available = bool(availability()) if callable(availability) else True
            except Exception as exc:
                provider_error = f"{type(exc).__name__}: {exc}"
                provider_available = False

        # Preserve the established deterministic fast path. If the existing
        # Brain already has a concrete text/format operation, the semantic
        # provider must not replace or duplicate that plan. Semantic provider
        # planning is used when deterministic understanding did not resolve
        # the request.
        if actions:
            provider_available = False

        if self.provider is not None and provider_available:
            provider_attempted = True
            try:
                try:
                    proposed = self.provider.plan(text, tool, context=context)
                except TypeError as exc:
                    # Backward-compatible provider contract: context is optional.
                    # Only retry when the provider rejects the newer keyword.
                    if "context" not in str(exc):
                        raise
                    proposed = self.provider.plan(text, tool)
                provider_returned = isinstance(proposed, dict)
            except Exception as exc:
                proposed = None
                provider_error = f"{type(exc).__name__}: {exc}"

            provider_goal_complete = bool(
                proposed.get("goal_complete")
                or proposed.get("goalComplete")
                or proposed.get("completed")
                or proposed.get("complete")
            ) if isinstance(proposed, dict) else False
            provider_actions = proposed.get("actions", []) if isinstance(proposed, dict) else []
            if isinstance(provider_actions, list):
                provider_added = False
                for item in provider_actions:
                    if not isinstance(item, dict):
                        continue
                    capability = str(item.get("capability") or item.get("operation") or "").strip()
                    arguments = item.get("arguments", {})
                    if not capability or not isinstance(arguments, dict):
                        continue
                    if capability not in caps:
                        continue
                    added = add(
                        capability,
                        arguments,
                        str(item.get("reason") or "Semantic model proposed this capability."),
                        "provider",
                    )
                    provider_added = provider_added or added
                provider_used = provider_added

        if provider_used:
            # Do not let legacy phrase rules add a conflicting operation after
            # the semantic model has produced a validated plan.
            pass
        elif continuation and provider_attempted:
            # Do not downgrade a goal-continuation turn to generic capability
            # inference when semantic planning failed. Stop safely instead.
            pass
        else:
            #
            # Phrases such as "what is inside this folder" and
            # "tell me what is in this directory" mean that the user wants the
            # directory entries, not merely metadata about the directory itself.
            # Keep this semantic resolution in the Brain rather than in the
            # Console or Executor.
            if self._asks_folder_contents(low, path_hint=self._extract_path(text, context)):
                folder_path = self._extract_path(text, context)
                if folder_path and "filesystem.list" in caps:
                    add(
                        "filesystem.list",
                        {"path": folder_path},
                        f"Mapped the request for the folder contents to filesystem.list using {folder_path!r}.",
                    )

            # V1.7-E: generic capability understanding for Body-native operations.
            # This is driven by capability IDs and operation semantics, not by
            # registering every natural-language phrase as a separate rule.
            for capability in caps:
                inferred = self._infer_body_capability(capability, text, low, context)
                if inferred:
                    add(capability, inferred["arguments"], inferred["reason"])

        return {
            "ok": True,
            "tool": tool["id"],
            "request": text,
            "actions": actions,
            "brain": "Hashtag Core V10.0.0",
            "mode": "central-autonomous-recovery",
            "confidence": min(0.99, 0.72 + 0.08 * len(actions) + (0.08 if inspection else 0)),
            "inspection": inspection,
            "needs_provider": not bool(actions),
            "provider_used": provider_used,
            "provider_goal_complete": provider_goal_complete,
            "provider_attempted": provider_attempted,
            "provider_returned": provider_returned,
            "provider_error": provider_error,
            "continuation": continuation,
            "needs_help": not bool(actions) and not provider_goal_complete,
            "message": "Hashtag understood the request and built a safe executable plan." if actions else "Hashtag could not safely map the request yet.",
            "reasoning": {
                "understood": bool(actions),
                "inspected_input": bool(inspection),
                "composed_capabilities": len(actions) > 1,
                "safe_execution_only": True,
                "recovery_enabled": True,
                "learning_enabled": bool(self.learner),
                "semantic_provider_used": provider_used,
                "provider_goal_complete": provider_goal_complete,
                "provider_attempted": provider_attempted,
                "provider_returned": provider_returned,
                "provider_error": provider_error,
                "continuation": continuation,
                "body_capability_inference": any(a.get("source") == "brain" and a.get("capability", "").split(".", 1)[0] in {"filesystem", "terminal", "process", "git", "github", "tests"} for a in actions),
            },
        }

    @staticmethod
    def _valid_action_arguments(capability, arguments):
        """Validate the minimum arguments required by physical capabilities.

        This is a capability-contract check, not a natural-language rule.
        Semantic providers may propose only executable actions with the
        minimum required resource arguments.
        """
        if not isinstance(arguments, dict):
            return False

        filesystem_targeted = {
            "filesystem.inspect",
            "filesystem.list",
            "filesystem.search",
            "filesystem.read",
            "filesystem.create",
            "filesystem.write",
            "filesystem.delete",
            "filesystem.move",
            "filesystem.copy",
        }

        if capability in filesystem_targeted:
            path = arguments.get("path") or arguments.get("root")
            if not path:
                return False

        if capability in {"repository.read_file", "repository.write_file"}:
            if not (arguments.get("file") or arguments.get("path") or arguments.get("file_path")):
                return False

        return True

    @staticmethod
    def _extract_path(text, context=None):
        context = context or {}
        path = context.get("path") or context.get("root")
        match = re.search(
            r'(?:"([^"]+)"|\'([^\']+)\'|((?:[A-Za-z]:\\|/)[^\s"<>|]+))',
            text or "",
        )
        if match:
            path = next((group for group in match.groups() if group), path)
        if path:
            return str(path).rstrip(".,;):?!").strip()
        return None

    @staticmethod
    def _asks_folder_contents(low, path_hint=None):
        # Strong folder/directory wording plus a request to see what it
        # contains.  "what is inside" is intentionally treated differently
        # from "inspect", because inspect is metadata-only.
        content_phrases = (
            "what is inside",
            "what's inside",
            "what is in",
            "what's in",
            "tell me what is inside",
            "tell me what's inside",
            "tell me what is in",
            "tell me what's in",
            "show me what is inside",
            "show me what's inside",
            "show me what is in",
            "show me what's in",
            "list what is inside",
            "list what's inside",
            "list what is in",
            "list what's in",
            "what files are inside",
            "what files are in",
            "what folders are inside",
            "what folders are in",
            "what files and folders are inside",
            "what files and folders are in",
            "which files are inside",
            "which files are in",
            "which folders are inside",
            "which folders are in",
            "which files and folders are inside",
            "which files and folders are in",
            "show files inside",
            "show files in",
            "show folders inside",
            "show folders in",
            "show files and folders inside",
            "show files and folders in",
            "list files inside",
            "list files in",
            "list folders inside",
            "list folders in",
            "list files and folders inside",
            "list files and folders in",
        )
        if any(phrase in low for phrase in content_phrases):
            return True

        # More flexible natural-language form:
        # a question asking what/which items are inside/in a folder should
        # resolve to filesystem.list rather than metadata-only inspect.
        folder_words = ("folder", "directory", "folders", "directories")
        question_words = ("what", "which", "show", "list", "tell me")
        item_words = ("file", "files", "folder", "folders", "directory", "directories", "contents", "items")
        has_folder = any(word in low for word in folder_words)
        has_question = any(word in low for word in question_words)
        has_items = any(word in low for word in item_words)
        has_location_word = "inside" in low or re.search(r"\bin\b", low) is not None

        if has_folder and has_question and has_items and has_location_word:
            return True

        # Do not infer a directory listing merely because an explicit path is
        # accompanied by the word "inside". A file path such as
        # C:\Hashtag-Test\hello.txt must remain eligible for semantic
        # resolution to filesystem.read.
        return False

    @staticmethod
    def _capability_ids(tool):
        result = set()
        for c in tool.get("capabilities", []):
            if isinstance(c, str):
                result.add(c)
            elif isinstance(c, dict) and c.get("id"):
                result.add(str(c["id"]))
        return result

    @staticmethod
    def _infer_body_capability(capability, text, low, context):
        """
        Generic natural-language -> Body capability inference.

        The capability ID is authoritative for the operation domain/action.
        Natural language is used to determine whether the user actually
        requested that operation.

        This deliberately avoids matching arbitrary words from capability
        descriptions, which could cause unrelated capabilities such as
        tests.run to win over filesystem.inspect.
        """
        parts = str(capability or "").lower().split(".")
        if len(parts) < 2:
            return None

        domain = parts[0]
        verb = parts[-1]

        context = context or {}

        # ------------------------------------------------------------
        # Generic semantic aliases
        # ------------------------------------------------------------

        verb_aliases = {
            "inspect": (
                "inspect",
                "check",
                "examine",
                "analyze",
                "analyse",
                "look at",
                "information about",
                "details about",
            ),
            "list": (
                "list",
                "enumerate",
                "show contents",
                "display contents",
                "contents of",
            ),
            "search": (
                "search",
                "find",
                "locate",
                "look for",
            ),
            "read": (
                "read",
                "open",
                "view",
                "show me the contents",
                "contents of",
            ),
            "create": (
                "create",
                "make",
                "new",
            ),
            "write": (
                "write",
                "save",
                "edit",
                "modify",
            ),
            "delete": (
                "delete",
                "remove",
                "erase",
            ),
            "move": (
                "move",
                "rename",
            ),
            "copy": (
                "copy",
                "duplicate",
            ),
            "execute": (
                "execute",
                "run",
                "launch",
            ),
        }

        domain_aliases = {
            "filesystem": (
                "file",
                "files",
                "folder",
                "folders",
                "directory",
                "directories",
                "path",
                "filesystem",
                "drive",
                "disk",
            ),
            "terminal": (
                "terminal",
                "command",
                "shell",
                "console",
            ),
            "process": (
                "process",
                "processes",
                "running process",
                "running processes",
            ),
            "git": (
                "git",
                "repository",
                "repo",
                "branch",
                "commit",
                "working tree",
                "workspace",
            ),
            "github": (
                "github",
                "repository",
                "repo",
                "pull request",
                "branch",
                "commit",
                "file",
            ),
            "tests": (
                "test",
                "tests",
                "pytest",
                "test suite",
                "unit test",
            ),
        }

        # ------------------------------------------------------------
        # Extract an explicit resource/path.
        # ------------------------------------------------------------

        path = context.get("path") or context.get("root")

        # Prefer quoted paths (which may contain spaces). For an unquoted
        # Windows/Unix path, stop at whitespace so trailing natural-language
        # instructions such as "and list its contents" are not swallowed.
        path_match = re.search(
            r'(?:"([^"]+)"|\'([^\']+)\'|((?:[A-Za-z]:\\|/)[^\s"<>|]+))',
            text,
        )

        if path_match:
            path = next(
                (group for group in path_match.groups() if group),
                path,
            )

        if path:
            path = str(path).rstrip(".,;):").strip()

        # ------------------------------------------------------------
        # Determine whether the requested verb is actually present.
        # ------------------------------------------------------------

        verb_phrases = verb_aliases.get(verb, (verb,))

        requested_verb = any(
            re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", low)
            for phrase in verb_phrases
        )

        # A multi-word phrase such as "show contents" can legitimately
        # contain punctuation/spacing that prevents the boundary regex.
        if not requested_verb:
            requested_verb = any(
                phrase in low
                for phrase in verb_phrases
                if " " in phrase
            )

        if not requested_verb:
            return None

        # ------------------------------------------------------------
        # Determine whether the request contains domain/resource evidence.
        # ------------------------------------------------------------

        domain_phrases = domain_aliases.get(domain, (domain,))

        requested_domain = any(
            re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", low)
            for phrase in domain_phrases
        )

        if not requested_domain:
            requested_domain = any(
                phrase in low
                for phrase in domain_phrases
                if " " in phrase
            )

        # An explicit filesystem path is very strong filesystem evidence.
        explicit_filesystem_path = bool(
            path and (
                re.match(r"^[A-Za-z]:\\", path)
                or path.startswith("/")
            )
        )

        if domain == "filesystem" and explicit_filesystem_path:
            requested_domain = True

        # ------------------------------------------------------------
        # Domain-specific requirements
        # ------------------------------------------------------------

        if domain == "filesystem":
            if not requested_domain:
                return None

            if verb in {
                "inspect",
                "list",
                "search",
                "read",
                "create",
                "write",
                "delete",
                "move",
                "copy",
            } and not path:
                return None

            if verb == "inspect":
                return {
                    "arguments": {"path": path},
                    "reason": (
                        f"Mapped the requested inspection to filesystem.inspect "
                        f"and extracted the filesystem path {path!r}."
                    ),
                }

            if verb == "list":
                return {
                    "arguments": {"path": path},
                    "reason": (
                        f"Mapped the requested listing to filesystem.list "
                        f"and extracted the filesystem path {path!r}."
                    ),
                }

            if verb == "search":
                return {
                    "arguments": {"path": path},
                    "reason": (
                        f"Mapped the requested filesystem search to "
                        f"filesystem.search using {path!r}."
                    ),
                }

            if verb == "read":
                return {
                    "arguments": {"path": path},
                    "reason": (
                        f"Mapped the requested read operation to "
                        f"filesystem.read using {path!r}."
                    ),
                }

            return {
                "arguments": {"path": path},
                "reason": (
                    f"Mapped the requested {verb} operation to the "
                    f"filesystem capability using {path!r}."
                ),
            }

        # ------------------------------------------------------------
        # Terminal
        # ------------------------------------------------------------

        if domain == "terminal":
            if not requested_domain:
                return None

            if verb == "inspect":
                return {
                    "arguments": {},
                    "reason": (
                        "Mapped the terminal inspection request to "
                        "the Executor terminal inspection capability."
                    ),
                }

            if verb == "execute":
                command = context.get("command")

                match = re.search(
                    r"(?:run|execute)\s+"
                    r"(?:this\s+)?"
                    r"(?:command\s+)?[:]?\s*(.+)$",
                    text,
                    re.I,
                )

                if match and not command:
                    command = match.group(1).strip()

                if not command:
                    return None

                return {
                    "arguments": {"command": str(command)},
                    "reason": (
                        "Mapped the explicitly requested command execution "
                        "to the Executor terminal capability."
                    ),
                }

            return None

        # ------------------------------------------------------------
        # Process
        # ------------------------------------------------------------

        if domain == "process":
            if verb == "inspect" and requested_domain:
                return {
                    "arguments": {},
                    "reason": (
                        "Mapped the request to the Executor process "
                        "inspection capability."
                    ),
                }

            return None

        # ------------------------------------------------------------
        # Git
        # ------------------------------------------------------------

        if domain == "git":
            if not requested_domain:
                return None

            if verb == "inspect":
                return {
                    "arguments": {},
                    "reason": (
                        "Mapped the repository/workspace inspection request "
                        "to the Executor Git inspection capability."
                    ),
                }

            return None

        # ------------------------------------------------------------
        # GitHub
        # ------------------------------------------------------------

        if domain == "github":
            if not requested_domain:
                return None

            if verb in {"read", "search", "inspect"}:
                return {
                    "arguments": {},
                    "reason": (
                        f"Mapped the request to the available GitHub "
                        f"{verb} capability."
                    ),
                }

            return None

        # ------------------------------------------------------------
        # Tests
        # ------------------------------------------------------------

        if domain == "tests":
            if verb != "run":
                return None

            # IMPORTANT:
            # Do not treat generic "run" as a test request.
            # There must be explicit test-domain evidence.
            if not any(
                re.search(
                    r"(?<!\w)" + re.escape(phrase) + r"(?!\w)",
                    low,
                )
                for phrase in domain_aliases["tests"]
            ):
                return None

            return {
                "arguments": {},
                "reason": (
                    "Mapped the explicit test request to the Executor "
                    "tests.run capability."
                ),
            }

        return None

    @staticmethod
    def _asks_remove_digits(low):
        return bool(re.search(r"\b(?:remove|delete|strip|erase)\s+(?:all|every|each)?\s*(?:number|numbers|digit|digits|numeric characters|0\s*[-â€“]\s*9)\b|\bno\s+(?:number|numbers|digit|digits)\b", low))

    @staticmethod
    def _asks_remove_letters(low):
        return bool(re.search(r"\b(?:remove|delete|strip|erase)\s+(?:all\s+)?letters\b", low))

    @staticmethod
    def _asks_remove_duplicates(low):
        return any(x in low for x in ("remove duplicates", "delete duplicates", "deduplicate"))

    @staticmethod
    def _asks_remove_number_only(low):
        return any(x in low for x in ("number-only lines", "number only lines", "numeric-only lines", "remove lines that contain only numbers"))

    @staticmethod
    def _asks_lower(low):
        return any(x in low for x in ("lowercase", "to lowercase", "lower case"))

    @staticmethod
    def _asks_upper(low):
        return any(x in low for x in ("uppercase", "to uppercase", "upper case"))

    @staticmethod
    def _separator(text):
        for s in ("->", "=>", "â†’", "|", ":", ";"):
            if s in text:
                return s
        return None

    @staticmethod
    def _delimiter(x):
        return {"colon": ":", "comma": ",", "semicolon": ";", "pipe": "|", "tab": "\t", "space": " "}.get(x, x)

    @staticmethod
    def _generic_remove_target(text):
        raw = (text or "").strip()
        if not raw:
            return None
        if re.search(r"\b(?:lines?|rows?|records?)\b", raw, re.I) and re.search(r"\b(?:remove|delete|strip|erase|eliminate|discard)\b", raw, re.I):
            return None
        raw = re.sub(r"\b(?:from|in|on|inside|throughout)\s+(?:the\s+)?(?:whole|entire|full|complete|text|file|document|input|content)\b.*$", "", raw, flags=re.I)
        m = re.search(r'\b(?:remove|delete|erase|strip|eliminate|discard)\s+(?:the\s+)?(?:text|word|phrase|value|string)\s+["â€œ\']?([^"â€\']+?)["â€\']?(?:\s*$|\s+(?:from|in|throughout)\b)', raw, re.I)
        if m:
            return m.group(1).strip()
        m = re.search(r'\b(?:remove|delete|erase|strip|eliminate|discard)\s+["â€œ\']?([^"â€\']+?)["â€\']?(?:\s*$|\s+(?:from|in|throughout)\b)', raw, re.I)
        return m.group(1).strip() if m else None

    def _infer_field_projection(self, text, inspection):
        if not inspection or inspection.get("fieldCount", 0) < 2:
            return None
        low = text.lower()
        requested = []
        for tok in re.findall(r"[a-zA-Z][a-zA-Z0-9_-]*", low):
            canon = FIELD_ALIASES.get(tok)
            if canon and canon not in requested:
                requested.append(canon)
        if len(requested) < 2 or not any(x in low for x in ("field", "keep", "convert", "want", "format", "only", "select", ":")):
            return None
        positions = []
        for field in requested:
            pos = None
            for item in inspection["firstFields"]:
                vals = [str(v).lower() for v in item["samples"]]
                aliases = [k for k, v in FIELD_ALIASES.items() if v == field]
                if any(any(a in s for a in aliases) for s in vals):
                    pos = item["position"]
                    break
            if pos is None and field == "username" and inspection["fieldCount"] >= 2:
                pos = 1
            if pos is None and field == "password" and inspection["fieldCount"] >= 2:
                pos = inspection["fieldCount"]
            if pos is not None:
                positions.append(pos)
        if len(positions) != len(requested):
            return None
        delim = inspection.get("delimiter") or ":"
        m = re.search(r'(?:user(?:name)?|pass(?:word)?)\s*([:|;,])\s*(?:user(?:name)?|pass(?:word)?)', text, re.I)
        if m:
            delim = m.group(1)
        return {
            "capability": "format.pick_fields",
            "arguments": {"fields": positions, "delimiter": delim, "inputDelimiter": inspection.get("delimiter") or delim},
            "reason": f"Inspected the sample fields and mapped {':'.join(requested)} to positions {positions}; keep only those fields with {delim!r}.",
        }

    def normalize_actions(self, actions):
        return [Operation.from_action(a) for a in actions]

