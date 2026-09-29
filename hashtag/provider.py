import json
import os
import re
import traceback
import urllib.request


class ModelProvider:
    """
    Semantic planning provider for Hashtag Core.

    The model proposes normalized capabilities only.
    It never executes operations.

    G9-S8 note:
    Small/local models such as qwen3:4b may put their entire completion
    into a reasoning field and leave message.content empty. Reasoning is
    deliberately never treated as executable JSON.
    """

    def __init__(self, endpoint="", model="", api_key=""):
        self.endpoint = endpoint or ""
        self.model = model or ""
        self.api_key = api_key or ""

    def available(self):
        return bool(self.endpoint and self.model)

    @staticmethod
    def _capability_id(item):
        if isinstance(item, str):
            return item.strip()

        if isinstance(item, dict):
            for key in ("id", "capability", "name", "operation"):
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()

        return ""

    def _advertised_capability_ids(self, tool):
        values = []
        seen = set()

        capabilities = tool.get("capabilities", []) if isinstance(tool, dict) else []

        if not isinstance(capabilities, list):
            return values

        for item in capabilities:
            capability = self._capability_id(item)
            if capability and capability not in seen:
                seen.add(capability)
                values.append(capability)

        return values

    @staticmethod
    def _content_to_text(content):
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    text = item.get("text")
                    if isinstance(text, str):
                        parts.append(text)

            return "".join(parts).strip()

        return ""

    @staticmethod
    def _repair_json_escapes(text):
        if not text:
            return ""
        # Match a backslash that is NOT followed by a valid JSON escape sequence:
        # valid JSON escape characters: " \ / b f n r t or u[0-9a-fA-F]{4}
        # In Windows paths, \H, \R, \h etc. are invalid escapes.
        pattern = r'\\(?!["\\/bfnrt]|u[0-9a-fA-F]{4})'
        return re.sub(pattern, r'\\\\', text)

    @staticmethod
    def _extract_json(content):
        text = ModelProvider._content_to_text(content)

        if not text:
            return None

        # Prefer a complete JSON object, trying original and repaired escapes.
        for candidate in (text, ModelProvider._repair_json_escapes(text)):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        # Also tolerate a fenced/object-wrapped response.
        start = text.find("{")
        end = text.rfind("}")

        if start < 0 or end <= start:
            return None

        slice_text = text[start:end + 1]
        for candidate in (slice_text, ModelProvider._repair_json_escapes(slice_text)):
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                pass

        return None

    CAPABILITY_ALIASES = {
        "repository.write": "repository.write_file",
        "repository.modify": "repository.write_file",
        "repository.modify_file": "repository.write_file",
        "repository.edit": "repository.write_file",
        "repository.edit_file": "repository.write_file",
        "repository.update": "repository.write_file",
        "repository.update_file": "repository.write_file",
        "repository.save_file": "repository.write_file",
        "repository.save": "repository.write_file",
        "write_file": "repository.write_file",
        "read_file": "repository.read_file",
        "list_files": "repository.list_files",
        "run_tests": "repository.run_tests",
        "repository.test": "repository.run_tests",
        "repository.tests": "repository.run_tests",
        "repository.pytest": "repository.run_tests",
        "repository.execute_tests": "repository.run_tests",
        "repository.read": "repository.read_file",
        "repository.list": "repository.list_files",
        "filesystem.write_file": "filesystem.write",
        "filesystem.read_file": "filesystem.read",
        "filesystem.list_files": "filesystem.list",
        "filesystem.run_tests": "tests.run",
        "github.write": "github.file.write",
        "github.write_file": "github.file.write",
        "github.create_file": "github.file.write",
        "github.create": "github.file.write",
        "github.edit_file": "github.file.write",
        "github.read": "github.file.read",
        "github.read_file": "github.file.read",
        "github.list": "github.files.list",
        "github.list_files": "github.files.list",
        "github.delete": "github.file.delete",
        "github.delete_file": "github.file.delete",
        "deploy_core": "github.deploy_core",
        "deploy": "github.deploy_core",
        "repository.deploy_core": "github.deploy_core",
        "github.deploy_core": "github.deploy_core",
        "github.sync": "github.deploy_core",
        "github.sync_core": "github.deploy_core",
        "sync_core": "github.deploy_core",
    }

    @classmethod
    def _normalize_action(cls, item, advertised):
        if not isinstance(item, dict):
            return None

        capability = (
            item.get("capability")
            or item.get("operation")
            or item.get("action")
            or item.get("tool")
        )

        if not isinstance(capability, str):
            return None

        capability = capability.strip()

        if capability not in advertised:
            aliased = cls.CAPABILITY_ALIASES.get(capability)
            if aliased and aliased in advertised:
                capability = aliased
            else:
                return None

        arguments = (
            item.get("arguments")
            if isinstance(item.get("arguments"), dict)
            else item.get("args")
            if isinstance(item.get("args"), dict)
            else item.get("parameters")
            if isinstance(item.get("parameters"), dict)
            else {}
        )

        args_dict = dict(arguments)

        # Normalize common argument aliases for repository/filesystem/github operations
        if capability in {"repository.write_file", "filesystem.write", "github.file.write"}:
            path_val = None
            for key in ("file", "path", "file_path", "filepath", "filename", "target"):
                if key in args_dict:
                    val = args_dict.pop(key)
                    if path_val is None:
                        path_val = val

            if path_val is not None:
                if capability.startswith("repository."):
                    args_dict["file"] = path_val
                else:
                    args_dict["path"] = path_val
            elif capability == "github.file.write":
                args_dict["path"] = "index.html"

            if "content" not in args_dict:
                for alt in ("text", "code", "file_content", "contents", "body"):
                    if alt in args_dict:
                        args_dict["content"] = args_dict.pop(alt)
                        break
            for alt in ("text", "code", "file_content", "contents", "body"):
                args_dict.pop(alt, None)

            if capability == "github.file.write" and "message" not in args_dict:
                args_dict["message"] = f"Update {args_dict.get('path', 'file')} via Hashtag"

        elif capability in {"repository.read_file", "filesystem.read", "github.file.read", "github.file.delete"}:
            path_val = None
            for key in ("file", "path", "file_path", "filepath", "filename", "target", "name"):
                if key in args_dict:
                    val = args_dict.pop(key)
                    if path_val is None:
                        path_val = val
            if path_val is None:
                for k, v in list(args_dict.items()):
                    if isinstance(v, str) and (v.endswith((".py", ".json", ".html", ".js", ".css", ".md", ".txt")) or "/" in v or "\\" in v):
                        path_val = args_dict.pop(k)
                        break

            if path_val is None and item.get("reason"):
                m = re.search(r"([\w\-./\\]+\.(?:py|html|css|js|json|md))", str(item["reason"]))
                if m:
                    path_val = m.group(1)

            if path_val is None:
                if capability.startswith("github."):
                    capability = "github.files.list"
                elif capability.startswith("repository."):
                    capability = "repository.list_files"
                else:
                    capability = "filesystem.list"
            else:
                if capability.startswith("repository."):
                    args_dict["file"] = path_val
                else:
                    args_dict["path"] = path_val

        elif capability == "github.files.list":
            args_dict.setdefault("path", "")


        elif capability in {"repository.run_tests", "tests.run"}:
            for key in ("path", "root", "repo"):
                if key in args_dict and "repository" not in args_dict:
                    args_dict["repository"] = args_dict[key]


        normalized = {
            "capability": capability,
            "arguments": args_dict,
        }

        reason = item.get("reason")
        if isinstance(reason, str) and reason.strip():
            normalized["reason"] = reason.strip()

        return normalized


    def _normalize_plan(self, proposed, advertised, request=None):
        if isinstance(proposed, list):
            proposed = {"actions": proposed, "goal_complete": False}
        elif not isinstance(proposed, dict):
            return None

        actions = proposed.get("actions")
        if actions is None and (
            "capability" in proposed
            or "operation" in proposed
            or "action" in proposed
            or "tool" in proposed
        ):
            actions = [proposed]

        if not isinstance(actions, list):
            return None

        goal_complete = bool(
            proposed.get("goal_complete")
            or proposed.get("goalComplete")
            or proposed.get("completed")
            or proposed.get("complete")
        )

        # An explicit goal-complete response is allowed to contain no next
        # action.  This is how the semantic model tells the orchestration
        # layer that the overall user goal has been satisfied.
        if not actions and not goal_complete:
            return None

        normalized = []
        local_repository = self._extract_local_repository_path(request)

        for item in actions:
            action = self._normalize_action(item, advertised)
            if action is None:
                return None

            # If the user explicitly supplied a local repository path and the
            # model selected a provider-neutral repository capability without
            # a target, carry that exact entity into the action. This prevents
            # an otherwise valid repository.inspect from being misrouted to
            # GitHub merely because the model omitted the argument.
            if local_repository:
                repo_name = os.path.basename(local_repository.rstrip(r"\/"))
                if action["capability"].startswith("repository."):
                    action["arguments"].setdefault("repository", local_repository)
                    action["arguments"].setdefault("provider", "local")
                    file_val = action["arguments"].get("file")
                    if isinstance(file_val, str) and repo_name:
                        p_norm = file_val.replace("\\", "/").lstrip("/")
                        if p_norm.lower().startswith(repo_name.lower() + "/"):
                            action["arguments"]["file"] = p_norm[len(repo_name) + 1:]
                elif action["capability"] == "tests.run":
                    action["arguments"].setdefault("path", local_repository)
                    action["arguments"].setdefault("roots", [local_repository])
                    action["arguments"].setdefault("repository", local_repository)
                elif action["capability"].startswith("filesystem."):
                    action["arguments"].setdefault("path", local_repository)
                    path_val = action["arguments"].get("path")
                    if isinstance(path_val, str) and repo_name:
                        p_norm = path_val.replace("\\", "/").lstrip("/")
                        if p_norm.lower().startswith(repo_name.lower() + "/"):
                            action["arguments"]["path"] = os.path.join(local_repository, p_norm[len(repo_name) + 1:])

            normalized.append(action)

        return {
            "actions": normalized,
            "goal_complete": goal_complete,
        }

    @staticmethod
    def _extract_local_repository_path(request):
        """Extract an explicit local repository path from the user request.

        This is entity extraction, not a phrase-specific command rule: the
        exact path supplied by the user becomes the repository target.
        """
        import re

        text = str(request or "")

        # Windows drive paths and common absolute POSIX paths.
        patterns = (
            r"(?i)([a-z]:\\[^\s\"'<>|]+)",
            r"(/(?:home|workspace|tmp)/[^\s\"'<>|]+)",
        )

        for pattern in patterns:
            match = re.search(pattern, text)
            if not match:
                continue

            value = match.group(1).rstrip(".,;:!?)]}\n\r")
            if value:
                return value

        return None

    @staticmethod
    def _is_local_repository_request(request):
        return ModelProvider._extract_local_repository_path(request) is not None

    def _build_prompt(self, request, advertised_capabilities, context=None):
        capabilities_json = json.dumps(
            advertised_capabilities,
            ensure_ascii=False,
        )

        context = context if isinstance(context, dict) else {}
        context_lines = []
        if isinstance(context, dict):
            step = context.get("step")
            if step is not None:
                context_lines.append(f"Current step: {step}")
            last_op = context.get("last_operation")
            if isinstance(last_op, dict):
                op_name = last_op.get("operation")
                target = (last_op.get("arguments") or {}).get("file") or (last_op.get("arguments") or {}).get("path")
                context_lines.append(f"Last executed operation: {op_name} (target: {target})")
            last_exec = context.get("last_execution")
            if isinstance(last_exec, dict):
                context_lines.append(f"Last execution status: {last_exec.get('status')}")
                if last_exec.get("error"):
                    context_lines.append(f"Last error: {last_exec.get('error')}")

            obs = context.get("observations") or []
            if obs:
                context_lines.append("\nRecent observations:")
                for o in obs[-4:]:
                    o_step = o.get("step")
                    o_op = (o.get("operation") or {}).get("operation")
                    o_tgt = (o.get("operation") or {}).get("arguments", {}).get("file") or (o.get("operation") or {}).get("arguments", {}).get("path")
                    o_stat = o.get("status")
                    o_out = str(o.get("output", "")).strip()
                    if o_op in ("repository.run_tests", "tests.run"):
                        if "failed" not in o_out.lower() and ("passed in" in o_out.lower() or "passed" in o_out.lower()):
                            context_lines.append(f"  - Step {o_step} ({o_op}): ALL TESTS PASSED! ({o_out[:200]})")
                        else:
                            # Provide rich failure diagnostics (assertions, tracebacks, error lines)
                            fail_snip = o_out
                            if "FAILURES" in fail_snip:
                                fail_snip = fail_snip[fail_snip.find("FAILURES"):]
                            context_lines.append(f"  - Step {o_step} ({o_op}): Status={o_stat}. Tests STILL FAILING:\n{fail_snip[:1500]}")
                    elif o_op in ("repository.read_file", "filesystem.read"):
                        context_lines.append(f"  - Step {o_step} ({o_op} {o_tgt}):\n    {o_out[:1200]}")
                    elif "FAILED" in o_out or "AssertionError" in o_out or o_stat == "error":
                        context_lines.append(f"  - Step {o_step} ({o_op} {o_tgt}): {o_out[:1200]}")
                    elif o_op in ("repository.write_file", "filesystem.write", "github.file.write") and o_stat == "success":
                        context_lines.append(f"  - Step {o_step} ({o_op} {o_tgt}): File write SUCCESSFUL! If the requested file operation is finished, set goal_complete: true and actions: [].")
                    else:
                        context_lines.append(f"  - Step {o_step} ({o_op} {o_tgt}): {o_stat}")

        context_text = "\n".join(context_lines)

        local_repository = self._is_local_repository_request(request)
        target_repo = ""
        if isinstance(context, dict):
            target_repo = context.get("target_repo") or context.get("repository") or ""

        domain_rules = ""
        if local_repository:
            domain_rules = """
GENERAL AUTONOMOUS REPAIR WORKFLOW (LOCAL REPOSITORY):
- You are an autonomous software engineering agent. Solve all issues dynamically across any programming language (Python, JavaScript, HTML, CSS, JSON, etc.).
- Prefer repository.* capabilities when they are advertised. Never choose github.* for a local path.
- CRITICAL RULE: NEVER modify test files (e.g. tests/*.py or test_*.py)! Tests are the ground-truth specification. You must fix the application source files being tested (e.g. app.py, config.json, index.html)!
- Follow the autonomous engineering cycle:
  1. If tests have not been executed yet, run `repository.run_tests` to observe failures.
  2. If tests failed, trace from the failure message and traceback to the defective implementation file:
     * If an error occurs loading or parsing a data file (e.g. config.json), read that file with `repository.read_file`.
     * If an error occurs in application code or functions (e.g. app.py), read that file with `repository.read_file`.
     * If an assertion checks markup or scripts in a web file (e.g. index.html), read that file with `repository.read_file`.
  3. Once you read an implementation file, your VERY NEXT ACTION MUST BE `repository.write_file` to write the corrected code to disk!
     Do NOT call `repository.run_tests` or re-read before writing the fix. You cannot verify a fix until you have written it with `repository.write_file`!
  4. In `repository.write_file`, supply arguments {"file": "<path>", "content": "<complete_corrected_content>"}. Always provide the complete, valid, syntactically correct file contents.
  5. After writing the fix, run `repository.run_tests` to verify which tests pass and observe any remaining failures.
  6. If other tests are still failing, repeat steps 2-5 for the remaining defective source files until all tests pass.
  7. When `repository.run_tests` passes (0 failures, returncode 0), the goal is completely satisfied: set "goal_complete": true and "actions": [].
"""
        else:
            domain_rules = f"""
NATURAL LANGUAGE & GITHUB AUTONOMOUS WORKFLOW:
- Target repository: {target_repo or "Active GitHub Repository"}
- You are Hashtag AI, an intelligent autonomous software engineer capable of understanding natural language requests across any programming language (HTML, CSS, JavaScript, Python, JSON, Markdown, etc.).
- When creating or editing files in GitHub:
  1. If the user asks to create or write a file (e.g., "Create a html file in github", "create login.html", "add hello.py"):
     Use `github.file.write` (or `repository.write_file`).
     Supply arguments: {{"path": "<filename>", "content": "<complete_working_code>", "message": "<commit_message>"}}.
     If the user does not specify a filename, choose an appropriate standard name (e.g. "index.html" for HTML, "main.py" for Python).
  2. Intelligent Code Understanding & Autonomous Correction:
     * If the user gave code that is syntactically broken, contains typos, unclosed tags/brackets, invalid commas, or incompatible syntax:
       DO NOT FAIL OR REJECT. Understand what the user wants to accomplish, REPAIR AND CORRECT the code completely, ensure full compatibility, and write the valid code to the file!
     * If the user describes changes or features without giving code, generate the full, elegant, production-ready code yourself!
     * Always provide complete, valid file content in "content" (never partial or pseudo-code).
  3. If the user asks to inspect or check existing repository files first, use `github.files.list` or `github.file.read`.
  4. If the user asks to move, deploy, or sync the entire Hashtag Core codebase from PC to GitHub: use `github.deploy_core` with arguments {{}}.
  5. After writing/updating the requested file on GitHub, if no further steps are needed, set "goal_complete": true and "actions": [].
"""

        return f"""
You are Hashtag AI's semantic capability planner.

Return ONLY one JSON object.
The first character must be {{ and the last character must be }}.
Do not output reasoning.
Do not output analysis.
Do not output markdown.
Do not output code.
Do not output shell commands.
Do not output commentary.

The JSON schema is:
{{
  "goal_complete": false,
  "actions": [
    {{
      "capability": "<CAPABILITY_NAME>",
      "arguments": {{}},
      "reason": "brief reason"
    }}
  ]
}}

Capability argument specifications:
- github.deploy_core: arguments {{}} (deploys the entire Hashtag Core codebase from PC to GitHub in one atomic commit)
- github.file.write: arguments {{"path": "<file_path>", "content": "<complete_code>", "message": "<commit_message>"}}
- github.file.read: arguments {{"path": "<file_path>"}}
- github.files.list: arguments {{"path": ""}}
- github.file.delete: arguments {{"path": "<file_path>", "message": "<commit_message>"}}
- github.backup.zip: arguments {{"output_path": "backup.zip"}}
- repository.read_file: arguments {{"file": "<path_to_file>"}} (e.g. {{"file": "tests/test_web.py"}} or {{"file": "config.json"}})
- repository.write_file: arguments {{"file": "<path_to_file>", "content": "<complete_file_content>"}}
- repository.run_tests: arguments {{"repository": "C:\\..."}} or empty {{}}
- repository.list_files: arguments {{}}

Set "goal_complete" to true ONLY when the supplied observations/evidence
show that the user's overall request has been completed. When the goal is
complete, return an empty actions array. Otherwise return the single next
safely observable action (or a small dependency-safe set of actions).

Rules:
1. Use only capabilities from the advertised list.
2. Put operation parameters inside "arguments".
3. Do not invent capabilities.
4. Do not invent files or paths; operate only on files existing in the repository or mentioned in test failures or user request.
5. After reading a defective file and diagnosing the bug, write the corrected file using repository.write_file or github.file.write.
6. Do not call repository.run_tests without first writing the code fixes, as unchanged files will produce the same test failure.
7. Keep the response concise.
8. The model's reasoning is not part of the output and must not be encoded into actions.
9. Use the current observations as evidence; never invent unseen repository facts.
10. When the user's task is fulfilled, declare goal_complete: true with an empty actions array.

Advertised capabilities:
{capabilities_json}
{domain_rules}

CURRENT EXECUTION CONTEXT / OBSERVATIONS:
{context_text}

USER REQUEST:
{request}
""".strip()

    def _request_model(self, prompt):
        try:
            max_tokens = int(os.getenv("HASHTAG_MODEL_MAX_TOKENS", "768"))
        except ValueError:
            max_tokens = 768

        try:
            timeout = float(os.getenv("HASHTAG_MODEL_TIMEOUT", "90"))
        except ValueError:
            timeout = 90.0

        max_tokens = max(1024, min(max_tokens, 4096))

        # If the configured endpoint is Ollama's OpenAI-compatible endpoint,
        # use Ollama's native chat endpoint so `think=false` and JSON format
        # are handled by Ollama itself.
        endpoint = self.endpoint
        if endpoint.rstrip("/").endswith("/v1/chat/completions"):
            endpoint = endpoint.rstrip("/")[:-len("/v1/chat/completions")] + "/api/chat"

        if endpoint.rstrip("/").endswith("/api/chat"):
            body = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt,
                    },
                    {
                        "role": "user",
                        "content": "Return the JSON plan now.",
                    },
                ],
                "stream": False,
                "think": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "repeat_penalty": 1.15,
                    "num_predict": max_tokens,
                },
            }
        else:
            body = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt,
                    }
                ],
                "temperature": 0.1,
                "max_tokens": max_tokens,
            }

        payload = None
        last_exc = None
        for attempt in range(3):
            try:
                if attempt > 0 and isinstance(body, dict) and "options" in body:
                    body["options"]["temperature"] = 0.2 + (attempt * 0.1)
                    body["options"]["repeat_penalty"] = 1.15 + (attempt * 0.05)

                req = urllib.request.Request(
                    endpoint,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                if self.api_key:
                    req.add_header("Authorization", "Bearer " + self.api_key)

                with urllib.request.urlopen(req, timeout=timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                break
            except urllib.error.HTTPError as exc:
                try:
                    err_body = exc.read().decode("utf-8")
                except Exception:
                    err_body = ""
                print(f"[OLLAMA HTTP ERROR {exc.code} attempt {attempt}]: {err_body}")
                last_exc = RuntimeError(f"Ollama {exc.code}: {err_body}")
                import time
                time.sleep(1.0)
            except Exception as exc:
                last_exc = exc
                import time
                time.sleep(1.0)

        if payload is None:
            raise last_exc

        # Normalize Ollama native /api/chat into the OpenAI-compatible shape
        # expected by the rest of Hashtag Core.
        if endpoint.rstrip("/").endswith("/api/chat"):
            message = payload.get("message", {})
            if isinstance(message, dict):
                return {
                    "choices": [
                        {
                            "index": 0,
                            "message": message,
                            "finish_reason": "stop" if payload.get("done", True) else "length",
                        }
                    ],
                    "ollama_native": True,
                    "raw": payload,
                }

        return payload

    def plan(self, request, tool, context=None):
        if not self.available():
            return None

        advertised = self._advertised_capability_ids(tool)

        if not advertised:
            return None

        prompt = self._build_prompt(request, advertised, context=context)

        try:
            payload = self._request_model(prompt)

            choices = payload.get("choices", [])
            if not isinstance(choices, list) or not choices:
                print(f"[PROVIDER DEBUG] No choices in model payload: {payload}")
                return None

            message = choices[0].get("message", {})
            if not isinstance(message, dict):
                print(f"[PROVIDER DEBUG] Invalid message in choices: {choices[0] if choices else None}")
                return None

            # IMPORTANT:
            # Never use message["reasoning"] as an executable plan.
            # qwen3:4b can spend its entire completion budget there.
            content = self._content_to_text(message.get("content", ""))

            if not content:
                print(f"[PROVIDER DEBUG] Empty content in model message: {message}")
                return None

            proposed = self._extract_json(content)
            if not proposed:
                print(f"[PROVIDER DEBUG] Failed to extract JSON from model content:\n{content}")
                return None

            plan = self._normalize_plan(
                proposed,
                set(advertised),
                request=request,
            )
            if plan is None:
                print(f"[PROVIDER DEBUG] Failed to normalize plan from proposed:\n{proposed}")
            return plan

        except Exception as exc:
            traceback.print_exc()
            raise

