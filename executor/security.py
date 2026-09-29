"""Security policy and path/operation guards for the Executor Body."""
from pathlib import Path

class SecurityError(RuntimeError): pass

SENSITIVE_PREFIXES = ("filesystem.", "terminal.", "process.", "git.modify", "github.branch.", "github.file.write", "github.commit.", "github.pull_request.")


def requires_permission(operation: str) -> bool:
    return operation.startswith(SENSITIVE_PREFIXES)


def ensure_path_allowed(path: str, allowed_roots: list[str]) -> Path:
    target = Path(path).expanduser().resolve()
    roots = [Path(r).expanduser().resolve() for r in allowed_roots]
    if not roots:
        raise SecurityError("No filesystem roots have been authorized")
    if not any(target == root or root in target.parents for root in roots):
        raise SecurityError(f"Path is outside authorized roots: {target}")
    return target
