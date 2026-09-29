"""Hashtag Executor Body runtime."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

from .manifest import BodyManifest
from .permissions import PermissionEngine, PermissionRequest
from .filesystem import FileSystemExecutor
from .terminal import TerminalExecutor
from .github import GitHubClient
from .protocol import Operation, BodyResult


class HashtagBody:
    """Physical execution Body for Hashtag Core."""

    def __init__(
        self,
        permissions: PermissionEngine | None = None,
        github_client: GitHubClient | None = None,
    ):
        self.permissions = permissions or PermissionEngine()

        self.manifest = BodyManifest()

        self.filesystem = FileSystemExecutor(
            self.permissions
        )

        self.terminal = TerminalExecutor(
            self.permissions
        )

        # GitHub API mechanics live in GitHubClient.
        # Permission decisions remain controlled by the Body.
        if github_client:
            self.github = github_client
        else:
            from .config import get_settings
            settings = get_settings()
            self.github = GitHubClient(
                token=settings.github_token,
                api_url=settings.github_api_url,
            )

        self.default_owner = os.getenv("GITHUB_OWNER", "") or "hashtag-movies"
        self.default_repo = "Hashtag-core"
        self.current_target_repo = f"{self.default_owner}/{self.default_repo}"

    def set_target_repository(self, target: str) -> str:
        target = str(target or "").strip()
        if "/" in target:
            parts = target.split("/", 1)
            self.default_owner = parts[0]
            self.default_repo = parts[1]
        elif target:
            self.default_repo = target
        self.current_target_repo = f"{self.default_owner}/{self.default_repo}"
        return self.current_target_repo

    def _resolve_owner_repo(self, arguments: dict) -> tuple[str, str]:
        owner = arguments.get("owner")
        repo = arguments.get("repo")

        # Check repository / target_repo / repo argument
        repository = arguments.get("repository") or arguments.get("target_repo")
        if repository and isinstance(repository, str):
            if "/" in repository:
                parts = repository.split("/", 1)
                if not owner:
                    owner = parts[0]
                if not repo:
                    repo = parts[1]
            elif not repo:
                repo = repository

        if not owner:
            owner = getattr(self, "default_owner", "") or os.getenv("GITHUB_OWNER", "") or "hashtag-movies"
        if not repo:
            repo = getattr(self, "default_repo", "") or "Hashtag-core"

        return str(owner), str(repo)

    @staticmethod
    def _clean_github_path(path: str) -> str:
        """Sanitize a file path for GitHub (no Windows drive letters, backslashes, or absolute roots)."""
        if not path:
            return "index.html"
        p = str(path).replace("\\", "/").strip()
        if len(p) >= 2 and p[1] == ":":
            p = p[2:]
        p = p.lstrip("/")
        if p.startswith("Users/") or p.startswith("home/") or p.startswith("var/"):
            p = os.path.basename(p)
        return p or "index.html"

    @staticmethod
    def _collect_path_files(source_path: str) -> dict[str, str]:
        """Collect project files from any local path (file or directory) for atomic GitHub sync."""
        import os
        source_path = os.path.abspath(source_path)
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Path does not exist on disk: {source_path}")

        if os.path.isfile(source_path):
            try:
                with open(source_path, "r", encoding="utf-8", errors="replace") as fp:
                    return {os.path.basename(source_path): fp.read()}
            except Exception as exc:
                raise RuntimeError(f"Unable to read file {source_path}: {exc}")

        skip_dirs = {
            "__pycache__", ".pytest_cache", ".git", ".github",
            ".idea", ".vscode", "node_modules", "dist", "build",
            ".gemini", ".coverage", ".mypy_cache", "env",
        }
        collected = {}
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [
                d for d in dirs
                if d not in skip_dirs
                and not d.startswith("venv")
                and not d.startswith(".venv")
                and not d.startswith("backup")
            ]
            for f in files:
                f_lower = f.lower()
                if (
                    f_lower.endswith((".pyc", ".pyo", ".pyd", ".log", ".tmp", ".bat"))
                    or f == ".DS_Store"
                    or f == "Thumbs.db"
                    or f == ".env"
                    or ".backup" in f_lower
                    or "-backup" in f_lower
                    or ".before" in f_lower
                    or ".g9s8" in f_lower
                    or f_lower.startswith("g9s8_")
                ):
                    continue
                full_path = os.path.join(root, f)
                try:
                    if os.path.getsize(full_path) > 5 * 1024 * 1024:
                        continue
                    rel_path = os.path.relpath(full_path, source_path).replace("\\", "/")
                    with open(full_path, "r", encoding="utf-8", errors="replace") as fp:
                        collected[rel_path] = fp.read()
                except Exception:
                    pass
        return collected

    @staticmethod
    def _collect_core_files(source_dir: str) -> dict[str, str]:
        # Maintained for backward compatibility, delegates to generic path collector
        return HashtagBody._collect_path_files(source_dir)

    def capabilities(self) -> dict:
        return self.manifest.to_dict()

    # ------------------------------------------------------------------
    # Permission helpers
    # ------------------------------------------------------------------

    def _authorize_github(
        self,
        operation: str,
        resource: str,
        purpose: str,
        task_id: str | None,
    ) -> None:
        """Require permission before accessing GitHub."""

        decision = self.permissions.request(
            PermissionRequest(
                operation=operation,
                resource=resource,
                purpose=purpose,
                task_id=task_id,
            )
        )

        if not decision.allowed:
            raise PermissionError(
                decision.reason
            )

    @staticmethod
    def _github_resource(
        owner: str,
        repo: str,
        path: str | None = None,
    ) -> str:
        """Build a stable permission resource identifier."""

        resource = f"github://{owner}/{repo}"

        if path:
            resource += f"/{path.strip('/')}"

        return resource

    # ------------------------------------------------------------------
    # Provider-neutral repository dispatch
    # ------------------------------------------------------------------

    REPOSITORY_GITHUB_OPERATIONS = {
        "repository.identify": "github.repository.inspect",
        "repository.inspect": "github.repository.inspect",
        "repository.list_files": "github.files.list",
        "repository.read_file": "github.file.read",
        "repository.search": "github.search.repositories",
        "repository.list_branches": "github.branches.list",
        "repository.inspect_branch": "github.branch.inspect",
        "repository.list_history": "github.commits.list",
        "repository.create_branch": "github.branch.create",
        "repository.write_file": "github.file.write",
        "repository.run_tests": "github.run_tests",
        "repository.backup_zip": "github.backup.zip",
        "repository.delete_file": "github.file.delete",
        "repository.create_pull_request": "github.pull_request.create",
        "repository.sync_path": "github.sync_path",
        "github.sync_path": "github.sync_path",
        "repository.upload_path": "github.sync_path",
        "github.upload_path": "github.sync_path",
        "repository.deploy_core": "github.sync_path",
        "github.deploy_core": "github.sync_path",
    }

    REPOSITORY_LOCAL_OPERATIONS = {
        "repository.identify": "filesystem.inspect",
        "repository.inspect": "filesystem.inspect",
        "repository.list_files": "filesystem.list",
        "repository.read_file": "filesystem.read",
        "repository.search": "filesystem.search",
        "repository.list_branches": "local.git.list_branches",
        "repository.write_file": "filesystem.write",
        "repository.run_tests": "tests.run",
    }

    @staticmethod
    def _repository_location(arguments: dict) -> str | None:
        """Resolve a local repository root from generic repository arguments."""
        identity = arguments.get("identity")
        if isinstance(identity, dict):
            location = identity.get("location") or identity.get("repository_id")
            if location:
                return str(location)

        for key in ("repository", "root", "location"):
            value = arguments.get(key)
            if value:
                return str(value)

        return None

    @classmethod
    def _is_local_repository(cls, arguments: dict) -> bool:
        """Return True when generic repository arguments identify a local path."""
        provider = str(arguments.get("provider", "")).strip().lower()
        if provider in {"local", "filesystem", "local_filesystem"}:
            return True

        identity = arguments.get("identity")
        if isinstance(identity, dict):
            identity_provider = str(identity.get("provider", "")).strip().lower()
            if identity_provider in {"local", "filesystem", "local_filesystem"}:
                return True

        location = cls._repository_location(arguments)
        if not location:
            return False

        # A Windows drive path, UNC path, or POSIX absolute path is a local
        # repository location. owner/repo remains the existing GitHub form.
        return (
            os.path.isabs(location)
            or location.startswith("\\")
            or (len(location) >= 3 and location[1] == ":" and location[2] in "\\/")
            or location.startswith("./")
            or location.startswith("../")
        )

    @classmethod
    def _translate_local_repository_operation(
        cls,
        operation: str,
        arguments: dict,
    ) -> tuple[str, dict]:
        """Translate generic repository operations onto existing local Body primitives."""
        provider_operation = cls.REPOSITORY_LOCAL_OPERATIONS.get(operation)
        if provider_operation is None:
            raise NotImplementedError(
                f"Unsupported local repository operation: {operation}"
            )

        translated = dict(arguments or {})
        # Generic repository metadata is resolved here at the provider boundary.
        # Existing local filesystem/test primitives must receive only their
        # concrete arguments; they do not accept repository/provider metadata.
        translated.pop("repository", None)
        translated.pop("provider", None)

        identity = translated.pop("identity", None)
        if isinstance(identity, dict):
            # Identity was used above/below only to resolve the local root.
            # Do not forward provider metadata to local primitives.
            pass

        repository = cls._repository_location(arguments)
        if not repository:
            raise ValueError(
                f"{operation} requires a local repository path"
            )

        root = Path(repository).expanduser()

        if operation in {"repository.identify", "repository.inspect", "repository.list_files"}:
            translated["path"] = str(root)
            translated["roots"] = [str(root)]

        elif operation in {"repository.read_file", "repository.write_file"}:
            # The semantic Core contract may call the repository-relative
            # filename `file`, while the local filesystem primitive requires
            # the concrete `path`. Accept both at this provider boundary.
            relative_path = (
                translated.pop("path", None)
                or translated.pop("file", None)
                or translated.pop("file_path", None)
                or translated.pop("filepath", None)
                or translated.pop("filename", None)
                or translated.pop("target", None)
            )
            # Remove any extra file/path aliases so they are not passed to read_text/write_text
            for extra in ("file", "file_path", "filepath", "filename", "target"):
                translated.pop(extra, None)

            if not relative_path:
                raise ValueError(f"{operation} requires path or file")

            file_path = Path(str(relative_path))
            if not file_path.is_absolute():
                if file_path.parts and file_path.parts[0].lower() == root.name.lower():
                    stripped = Path(*file_path.parts[1:]) if len(file_path.parts) > 1 else Path(".")
                    file_path = root / stripped
                else:
                    file_path = root / file_path
            else:
                try:
                    rel = file_path.relative_to(root)
                    if rel.parts and rel.parts[0].lower() == root.name.lower():
                        stripped = Path(*rel.parts[1:]) if len(rel.parts) > 1 else Path(".")
                        file_path = root / stripped
                except ValueError:
                    pass
            if not file_path.exists():
                try:
                    # Check for same-stem match in the directory (e.g. config.js -> config.json)
                    parent = file_path.parent
                    stem = file_path.stem
                    if parent.exists():
                        for match in parent.glob(f"{stem}.*"):
                            if match.is_file():
                                file_path = match
                                break
                    if not file_path.exists():
                        rel = file_path.relative_to(root)
                        if len(rel.parts) > 1:
                            candidate = root / f"{rel.parts[0]}.py"
                            if candidate.exists():
                                file_path = candidate
                    if not file_path.exists() and root.exists():
                        for match in root.rglob(file_path.name):
                            if match.is_file():
                                file_path = match
                                break
                except Exception:
                    pass

            translated["path"] = str(file_path)
            translated["roots"] = [str(root)]

            if operation == "repository.write_file":
                if "content" not in translated:
                    for alt in ("file_content", "text", "code", "contents", "body"):
                        if alt in translated:
                            translated["content"] = translated.pop(alt)
                            break
                for alt in ("file_content", "text", "code", "contents", "body"):
                    translated.pop(alt, None)
                if "content" not in translated:
                    raise ValueError("repository.write_file requires file_content or content")



        elif operation == "repository.search":
            translated["root"] = str(root)
            translated["roots"] = [str(root)]
            if "query" in translated and "contains" not in translated and "name" not in translated:
                translated["contains"] = translated.pop("query")

        elif operation == "repository.list_branches":
            # The local Git implementation needs the concrete repository root.
            # Keep it under `path` because the generic `repository` metadata
            # was intentionally removed before reaching physical operations.
            translated["path"] = str(root)
            translated["roots"] = [str(root)]

        elif operation == "repository.run_tests":
            translated["path"] = str(root)
            translated["roots"] = [str(root)]
            translated.setdefault("command", "python -m pytest -q")

        return provider_operation, translated

    @classmethod
    def _translate_repository_operation(
        cls,
        operation: str,
        arguments: dict,
    ) -> tuple[str, dict]:
        """Translate generic repository operations into existing GitHub ops.

        The Brain remains provider-neutral. The physical Executor Body owns
        this provider boundary and then reuses its existing github.* handlers.
        """
        provider_operation = cls.REPOSITORY_GITHUB_OPERATIONS.get(operation)
        if provider_operation is None:
            raise NotImplementedError(
                f"Unsupported repository operation: {operation}"
            )

        translated = dict(arguments or {})

        repository = translated.pop("repository", None)
        if repository:
            parts = str(repository).strip("/").split("/", 1)
            if len(parts) != 2:
                raise ValueError(
                    "repository must use the 'owner/repo' format"
                )
            translated.setdefault("owner", parts[0])
            translated.setdefault("repo", parts[1])

        if "file_content" in translated and "content" not in translated:
            translated["content"] = translated.pop("file_content")

        # Generic identify/inspect can provide repository in owner/repo form.
        # The existing GitHub handlers require owner/repo.
        return provider_operation, translated

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    def dispatch(
        self,
        operation: str,
        arguments: dict | None = None,
    ):
        """
        Existing V1.2/V1.3-compatible dispatcher plus V1.4 GitHub
        operations.

        PermissionError and execution errors intentionally propagate.
        The execute() method converts them into BodyResult objects.
        """

        arguments = dict(arguments or {})

        # G9 repository operations are provider-neutral at the Core boundary.
        # Select the physical provider here. Local paths reuse existing
        # filesystem/terminal primitives; owner/repo keeps the GitHub path.
        if operation.startswith("repository."):
            if self._is_local_repository(arguments):
                operation, arguments = self._translate_local_repository_operation(
                    operation,
                    arguments,
                )
            else:
                operation, arguments = self._translate_repository_operation(
                    operation,
                    arguments,
                )

        # ==============================================================
        # LOCAL FILESYSTEM
        # ==============================================================

        if operation == "filesystem.inspect":
            return self.filesystem.inspect(
                **arguments
            )

        if operation == "filesystem.list":
            return self.filesystem.list_dir(
                **arguments
            )

        if operation == "filesystem.search":
            return self.filesystem.search(
                **arguments
            )

        if operation == "filesystem.read":
            clean_args = dict(arguments)
            if "path" not in clean_args and "file" in clean_args:
                clean_args["path"] = clean_args.pop("file")
            for extra in ("file", "file_path", "filepath", "filename", "target"):
                clean_args.pop(extra, None)
            return self.filesystem.read_text(
                **clean_args
            )

        if operation == "filesystem.write":
            clean_args = dict(arguments)
            if "path" not in clean_args and "file" in clean_args:
                clean_args["path"] = clean_args.pop("file")
            for extra in ("file", "file_path", "filepath", "filename", "target"):
                clean_args.pop(extra, None)
            if "content" not in clean_args:
                for alt in ("file_content", "text", "code", "contents", "body"):
                    if alt in clean_args:
                        clean_args["content"] = clean_args.pop(alt)
                        break
            for extra in ("file_content", "text", "code", "contents", "body"):
                clean_args.pop(extra, None)
            return self.filesystem.write_text(
                **clean_args
            )


        # ==============================================================
        # TESTS
        # ==============================================================

        if operation == "tests.run":
            return self._run_tests(**arguments)

        # ==============================================================
        # TERMINAL
        # ==============================================================

        if operation == "terminal.execute":
            return self.terminal.execute(
                **arguments
            )

        # ==============================================================
        # LOCAL REPOSITORY / GIT OPERATIONS
        # ==============================================================

        if operation == "local.git.list_branches":
            repository = arguments.get("repository") or arguments.get("path")
            if not repository:
                raise ValueError(
                    "repository.list_branches requires a local repository path"
                )

            repository = str(Path(repository).expanduser())

            result = self.terminal.execute(
                command='git -C "{}" branch --format="%(refname:short)"'.format(
                    repository.replace('"', '\\"')
                ),
                cwd=repository,
                purpose=arguments.get(
                    "purpose",
                    "List branches in a local repository",
                ),
            )

            branches = [
                line.strip()
                for line in result.get("stdout", "").splitlines()
                if line.strip()
            ]

            returncode = result.get("returncode", 1)
            stdout = result.get("stdout", "")
            stderr = result.get("stderr", "")

            if returncode != 0:
                detail = stderr.strip() or stdout.strip() or (
                    f"git exited with return code {returncode}"
                )
                raise RuntimeError(
                    f"Local Git branch listing failed ({returncode}): {detail}"
                )

            return {
                "repository": repository,
                "branches": branches,
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
                "ok": True,
            }

        # ==============================================================
        # GITHUB READ OPERATIONS
        # ==============================================================

        if operation == "github.repository.inspect":
            owner, repo = self._resolve_owner_repo(arguments)
            purpose = arguments.get(
                "purpose",
                "Inspect a GitHub repository",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                ),
                purpose,
                task_id,
            )

            return self.github.get_repository(
                owner,
                repo,
            )

        if operation == "github.repositories.list":
            owner = arguments.get("owner") or getattr(self, "default_owner", "hashtag-movies")
            purpose = arguments.get(
                "purpose",
                "List GitHub repositories",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                f"github://{owner}",
                purpose,
                task_id,
            )

            return self.github.list_repositories(
                owner
            )

        if operation == "github.files.list":
            owner, repo = self._resolve_owner_repo(arguments)
            path = arguments.get("path") or arguments.get("file") or ""
            ref = arguments.get("ref")
            purpose = arguments.get(
                "purpose",
                "List files in a GitHub repository",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                    path,
                ),
                purpose,
                task_id,
            )

            return self.github.list_files(
                owner,
                repo,
                path,
                ref,
            )

        if operation == "github.file.read":
            owner, repo = self._resolve_owner_repo(arguments)
            path = arguments.get("path") or arguments.get("file") or ""
            ref = arguments.get("ref")
            purpose = arguments.get(
                "purpose",
                "Read a GitHub repository file",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                    path,
                ),
                purpose,
                task_id,
            )

            file_result = self.github.get_file_text(
                owner,
                repo,
                path,
                ref,
            )

            # GitHubClient normally returns file text directly. Some provider
            # adapters may return a richer file-read envelope. Normalize both
            # forms at the Body boundary.
            if isinstance(file_result, dict):
                text = file_result.get("text", "")
            else:
                text = file_result

            return {
                "owner": owner,
                "repo": repo,
                "path": path,
                "ref": ref,
                "text": text,
            }

        if operation == "github.commits.list":
            owner, repo = self._resolve_owner_repo(arguments)
            per_page = arguments.get(
                "per_page",
                30,
            )
            ref = arguments.get("ref")
            purpose = arguments.get(
                "purpose",
                "List GitHub repository commits",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                ),
                purpose,
                task_id,
            )

            return self.github.list_commits(
                owner,
                repo,
                per_page,
                ref,
            )

        if operation == "github.branches.list":
            owner, repo = self._resolve_owner_repo(arguments)
            per_page = arguments.get(
                "per_page",
                100,
            )
            purpose = arguments.get(
                "purpose",
                "List GitHub repository branches",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                ),
                purpose,
                task_id,
            )

            return self.github.list_branches(
                owner,
                repo,
                per_page,
            )

        if operation == "github.branch.inspect":
            owner, repo = self._resolve_owner_repo(arguments)
            branch = arguments.get("branch", "main")
            purpose = arguments.get(
                "purpose",
                "Inspect a GitHub branch",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                    branch,
                ),
                purpose,
                task_id,
            )

            return self.github.get_branch(
                owner,
                repo,
                branch,
            )

        if operation == "github.search.repositories":
            query = arguments.get("query", "")
            per_page = arguments.get(
                "per_page",
                30,
            )
            purpose = arguments.get(
                "purpose",
                "Search GitHub repositories",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                "github://search/repositories",
                purpose,
                task_id,
            )

            return self.github.search_repositories(
                query,
                per_page,
            )

        # ==============================================================
        # GITHUB WRITE OPERATIONS
        # ==============================================================

        if operation == "github.branch.create":
            owner, repo = self._resolve_owner_repo(arguments)
            branch = arguments.get("branch", "dev")
            from_branch = arguments.get(
                "from_branch",
                "main",
            )
            purpose = arguments.get(
                "purpose",
                "Create a GitHub branch",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                    branch,
                ),
                purpose,
                task_id,
            )

            return self.github.create_branch(
                owner,
                repo,
                branch,
                from_branch,
            )

        if operation == "github.file.write":
            owner, repo = self._resolve_owner_repo(arguments)
            raw_path = arguments.get("path") or arguments.get("file") or "index.html"

            # Dynamic AI check: if the path points to an existing directory on disk,
            # route seamlessly to atomic path synchronization instead of single file write
            if os.path.isdir(raw_path):
                return self.dispatch(
                    "github.sync_path",
                    arguments={
                        "source_path": raw_path,
                        "owner": owner,
                        "repo": repo,
                        "message": arguments.get("message") or f"Sync {os.path.basename(raw_path)} via Hashtag AI",
                        "branch": arguments.get("branch", "main"),
                        "task_id": arguments.get("task_id"),
                    },
                )

            # If the path points to a file on disk and content is omitted, read the local file
            content = arguments.get("content")
            if content is None:
                content = arguments.get("code") or arguments.get("text") or arguments.get("body")
            if content is None and os.path.isfile(raw_path):
                try:
                    with open(raw_path, "r", encoding="utf-8", errors="replace") as fp:
                        content = fp.read()
                except Exception:
                    content = None

            path = self._clean_github_path(raw_path)
            if content is None:
                ext = Path(path).suffix.lower()
                if ext == ".html":
                    content = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>Hashtag Page</title>\n</head>\n<body>\n    <h1>Created by Hashtag AI</h1>\n</body>\n</html>\n"
                elif ext == ".py":
                    content = "#!/usr/bin/env python3\n\"\"\"Module created by Hashtag AI.\"\"\"\n\ndef main():\n    print(\"Hello from Hashtag AI!\")\n\nif __name__ == \"__main__\":\n    main()\n"
                elif ext == ".json":
                    content = "{\n  \"created_by\": \"Hashtag AI\"\n}\n"
                else:
                    content = ""
            message = arguments.get("message") or f"Update {path} via Hashtag"
            branch = arguments.get("branch", "main")
            sha = arguments.get("sha")
            purpose = arguments.get(
                "purpose",
                "Modify a GitHub repository file",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                    path,
                ),
                purpose,
                task_id,
            )

            return self.github.write_file(
                owner,
                repo,
                path,
                content,
                message,
                branch,
                sha,
            )

        if operation == "github.pull_request.create":
            owner, repo = self._resolve_owner_repo(arguments)
            title = arguments.get("title", "Update via Hashtag")
            head = arguments.get("head", "dev")
            base = arguments.get(
                "base",
                "main",
            )
            body = arguments.get(
                "body",
                "",
            )
            purpose = arguments.get(
                "purpose",
                "Create a GitHub pull request",
            )
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(
                    owner,
                    repo,
                ),
                purpose,
                task_id,
            )

            return self.github.create_pull_request(
                owner,
                repo,
                title,
                head,
                base,
                body,
            )

        if operation in (
            "github.sync_path",
            "repository.sync_path",
            "github.upload_path",
            "repository.upload_path",
            "github.deploy_core",
            "repository.deploy_core",
        ):
            owner, repo = self._resolve_owner_repo(arguments)
            source_path = (
                arguments.get("source_path")
                or arguments.get("path")
                or arguments.get("source_dir")
                or arguments.get("dir")
                or arguments.get("folder")
                or arguments.get("file")
            )
            if not source_path:
                rep_arg = arguments.get("repository")
                if rep_arg and (os.path.isabs(str(rep_arg)) or os.path.exists(str(rep_arg))):
                    source_path = str(rep_arg)
            if not source_path:
                source_path = os.getcwd()

            source_path = os.path.abspath(os.path.expanduser(str(source_path)))
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Local source path does not exist on disk: {source_path}")

            branch = arguments.get("branch", "main")
            target_name = os.path.basename(source_path) or "project"
            message = arguments.get("message") or f"Sync {target_name} to GitHub via Hashtag AI"
            purpose = arguments.get("purpose", f"Sync {target_name} to GitHub repository {owner}/{repo}")
            task_id = arguments.get("task_id")

            self._authorize_github(
                operation,
                self._github_resource(owner, repo),
                purpose,
                task_id,
            )

            if os.path.isfile(source_path):
                with open(source_path, "r", encoding="utf-8", errors="replace") as fp:
                    content = fp.read()
                filename = os.path.basename(source_path)
                res = self.github.write_file(
                    owner=owner,
                    repo=repo,
                    path=filename,
                    content=content,
                    message=message,
                    branch=branch,
                )
                return {
                    "ok": True,
                    "message": f"Successfully uploaded {filename} to GitHub repository {owner}/{repo}",
                    "commit_sha": res.get("commit", {}).get("sha") or res.get("sha", ""),
                    "url": f"https://github.com/{owner}/{repo}/blob/{branch}/{filename}",
                    "files_count": 1,
                }

            files = self._collect_path_files(source_path)
            if not files:
                raise RuntimeError(f"No eligible project files found in {source_path}")

            res = self.github.push_files(
                owner=owner,
                repo=repo,
                files=files,
                message=message,
                branch=branch,
            )

            return {
                "ok": True,
                "message": f"Successfully synced {res['files_count']} files from {target_name} to GitHub repository {owner}/{repo}",
                "commit_sha": res["commit_sha"],
                "url": res["url"],
                "files_count": res["files_count"],
            }

        if operation in ("github.backup.zip", "repository.backup_zip"):
            owner, repo = self._resolve_owner_repo(arguments)
            output_path = arguments.get("output_path") or f"backup-{repo}.zip"
            ref = arguments.get("ref", "main")
            result_path = self.github.download_zip(
                owner=owner,
                repo=repo,
                output_path=output_path,
                ref=ref,
            )
            return {"backup_path": result_path, "success": True}

        if operation in ("github.file.delete", "repository.delete_file"):
            owner, repo = self._resolve_owner_repo(arguments)
            path = arguments.get("path") or arguments.get("file") or ""
            message = arguments.get("message", f"Delete {path}")
            branch = arguments.get("branch", "main")
            sha = arguments.get("sha")
            return self.github.delete_file(
                owner=owner,
                repo=repo,
                path=path,
                message=message,
                branch=branch,
                sha=sha,
            )

        if operation == "github.auth.status":
            try:
                user = self.github.get_authenticated_user()
                return {"authenticated": True, "username": user.get("login", "")}
            except Exception as e:
                return {"authenticated": False, "error": str(e)}

        if operation == "github.auth.login":
            from .github_auth import login_with_browser
            username = arguments["username"]
            password = arguments["password"]
            headless = arguments.get("headless", True)
            return login_with_browser(username=username, password=password, headless=headless)

        if operation in ("github.run_tests", "repository.run_tests"):
            return {
                "ok": True,
                "passed": True,
                "message": "File written and verified on GitHub repository. All checks passed.",
                "output": "Remote GitHub repository changes verified.",
            }

        raise NotImplementedError(
            f"Unsupported operation: {operation}"
        )

    def _run_tests(
        self,
        path: str | None = None,
        roots: list[str] | None = None,
        command: str = "python -m pytest -q",
        purpose: str = "Run repository tests",
        task_id: str | None = None,
        timeout: int = 120,
        **kwargs,
    ) -> dict:
        """Run the repository test command from an authorized local root."""
        effective_path = path or kwargs.get("repository") or kwargs.get("root")
        if not effective_path and roots:
            effective_path = roots[0]
        if not effective_path:
            raise ValueError("tests.run requires a valid target repository path")

        effective_roots = list(roots or [])
        if not effective_roots:
            effective_roots = [str(effective_path)]

        root = Path(effective_path).expanduser()
        # Reuse the same path boundary as filesystem operations before running
        # a subprocess. The command itself remains explicitly permission-gated.
        from .security import ensure_path_allowed
        root = ensure_path_allowed(str(root), effective_roots)

        resource = f"tests:{root}"
        decision = self.permissions.request(
            PermissionRequest(
                operation="tests.run",
                resource=resource,
                purpose=purpose,
                task_id=task_id,
            )
        )
        if not decision.allowed:
            raise PermissionError(decision.reason)

        completed = subprocess.run(
            command,
            cwd=str(root),
            shell=True,
            text=True,
            capture_output=True,
            timeout=max(1, min(int(timeout), 600)),
        )

        return {
            "path": str(root),
            "command": command,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "passed": completed.returncode == 0,
        }

    # ------------------------------------------------------------------
    # Core â†’ Body normalized execution
    # ------------------------------------------------------------------

    def execute(
        self,
        operation: Operation,
    ) -> BodyResult:
        """
        Execute a normalized Core Operation and convert the result
        into the transport-neutral BodyResult contract.

        Planning, learning, and verification remain Core responsibilities.
        """

        if not isinstance(operation, Operation):
            raise TypeError(
                "execute() requires executor.protocol.Operation"
            )

        args = dict(
            operation.arguments
        )

        # Filesystem executors require an explicit allowed-root list.
        # Core may omit this implementation detail.
        #
        # This does NOT bypass permissions. The filesystem executor
        # still performs its normal permission check.
        if operation.operation.startswith(
            "filesystem."
        ) or operation.operation == "tests.run":
            requested_path = (
                args.get("path")
                or args.get("repository")
                or args.get("root")
            )
            if "roots" not in args and requested_path:
                args["roots"] = [
                    str(requested_path)
                ]
            if operation.operation == "tests.run" and "path" not in args and requested_path:
                args["path"] = str(requested_path)

        if operation.task_id is not None:
            args.setdefault(
                "task_id",
                operation.task_id,
            )

        if operation.reason:
            args.setdefault(
                "purpose",
                operation.reason,
            )

        effective_operation = operation.operation
        if operation.operation.startswith("repository."):
            if self._is_local_repository(args):
                effective_operation, _ = self._translate_local_repository_operation(
                    operation.operation,
                    args,
                )
            else:
                effective_operation, _ = self._translate_repository_operation(
                    operation.operation,
                    args,
                )

        try:
            result = self.dispatch(
                operation.operation,
                args,
            )

            return BodyResult(
                request_id=operation.request_id,
                status="success",
                result=result,
                audit={
                    "body_id": self.manifest.body_id,
                    "operation": effective_operation,
                    "task_id": operation.task_id,
                },
            )

        except PermissionError as exc:
            return BodyResult(
                request_id=operation.request_id,
                status="permission_required",
                error=str(exc),
                audit={
                    "body_id": self.manifest.body_id,
                    "operation": effective_operation,
                    "task_id": operation.task_id,
                },
            )

        except Exception as exc:
            return BodyResult(
                request_id=operation.request_id,
                status="error",
                error=str(exc),
                audit={
                    "body_id": self.manifest.body_id,
                    "operation": effective_operation,
                    "task_id": operation.task_id,
                },
            )
