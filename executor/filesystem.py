"""Permission-gated local filesystem inspection and read operations."""
from pathlib import Path
from .permissions import PermissionEngine, PermissionRequest
from .security import ensure_path_allowed


class FileSystemExecutor:
    def __init__(self, permissions: PermissionEngine):
        self.permissions = permissions

    def _authorize(self, operation: str, resource: str, purpose: str, task_id: str | None):
        d = self.permissions.request(PermissionRequest(operation, resource, purpose, task_id=task_id))
        if not d.allowed:
            raise PermissionError(d.reason)

    def inspect(self, path: str, roots: list[str], purpose: str = "Inspect a local file or folder", task_id: str | None = None) -> dict:
        p = ensure_path_allowed(path, roots)
        self._authorize("filesystem.inspect", str(p), purpose, task_id)
        exists = p.exists()
        if not exists:
            return {"path": str(p), "exists": False, "is_file": False, "is_dir": False, "size": None}
        st = p.stat()
        return {"path": str(p), "exists": True, "is_file": p.is_file(), "is_dir": p.is_dir(), "size": st.st_size}

    def list_dir(self, path: str, roots: list[str], purpose: str = "List a local folder", task_id: str | None = None, recursive: bool = False, max_entries: int = 500) -> dict:
        p = ensure_path_allowed(path, roots)
        self._authorize("filesystem.list", str(p), purpose, task_id)
        if not p.exists() or not p.is_dir():
            raise NotADirectoryError(str(p))
        max_entries = max(1, min(int(max_entries), 5000))
        iterator = p.rglob("*") if recursive else p.iterdir()
        entries = []
        truncated = False
        for child in iterator:
            # Never follow directory symlinks outside the authorized root.
            try:
                child_resolved = child.resolve()
                ensure_path_allowed(str(child_resolved), roots)
            except Exception:
                continue
            if len(entries) >= max_entries:
                truncated = True
                break
            try:
                is_dir = child.is_dir()
                size = None if is_dir else child.stat().st_size
            except OSError:
                is_dir, size = False, None
            entries.append({"name": child.name, "path": str(child), "is_dir": is_dir, "size": size})
        entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
        return {"path": str(p), "entries": entries, "count": len(entries), "truncated": truncated, "recursive": recursive}

    def search(self, root: str, roots: list[str], name: str | None = None, contains: str | None = None,
               purpose: str = "Search authorized local files", task_id: str | None = None,
               max_results: int = 200) -> dict:
        p = ensure_path_allowed(root, roots)
        self._authorize("filesystem.search", str(p), purpose, task_id)
        if not p.exists() or not p.is_dir():
            raise NotADirectoryError(str(p))
        max_results = max(1, min(int(max_results), 2000))
        needle = (name or "").lower()
        text_needle = (contains or "").lower()
        results = []
        truncated = False
        for child in p.rglob("*"):
            try:
                ensure_path_allowed(str(child.resolve()), roots)
            except Exception:
                continue
            if needle and needle not in child.name.lower():
                continue
            if text_needle and child.is_file():
                try:
                    if text_needle not in child.read_text(encoding="utf-8", errors="ignore").lower():
                        continue
                except (OSError, UnicodeError):
                    continue
            elif text_needle and child.is_dir():
                continue
            if len(results) >= max_results:
                truncated = True
                break
            try:
                size = None if child.is_dir() else child.stat().st_size
            except OSError:
                size = None
            results.append({"name": child.name, "path": str(child), "is_dir": child.is_dir(), "size": size})
        results.sort(key=lambda x: x["path"].lower())
        return {"root": str(p), "results": results, "count": len(results), "truncated": truncated}

    def read_text(self, path: str, roots: list[str], purpose: str = "Read a local text file", task_id: str | None = None, max_bytes: int = 5_000_000) -> dict:
        p = ensure_path_allowed(path, roots)
        self._authorize("filesystem.read", str(p), purpose, task_id)
        if not p.is_file():
            raise FileNotFoundError(str(p))
        max_bytes = max(1, min(int(max_bytes), 20_000_000))
        data = p.read_bytes()
        truncated = len(data) > max_bytes
        text = data[:max_bytes].decode("utf-8", errors="replace")
        return {"path": str(p), "text": text, "bytes": len(data), "truncated": truncated}
    def write_text(
        self,
        path: str,
        content: str,
        roots: list[str],
        purpose: str = "Write a local text file",
        task_id: str | None = None,
        encoding: str = "utf-8",
    ) -> dict:
        """Permission-gated write of a UTF-8 text file."""
        p = ensure_path_allowed(path, roots)
        self._authorize("filesystem.write", str(p), purpose, task_id)

        if p.exists() and p.is_dir():
            raise IsADirectoryError(str(p))

        data = str(content).encode(encoding)
        p.write_bytes(data)

        return {
            "path": str(p),
            "bytes": len(data),
            "written": True,
        }

