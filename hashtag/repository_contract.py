"""Hashtag Gate 9 Step 1: generic repository identity and inspection contracts.

This module describes a repository as an environment that Hashtag can inspect.
It intentionally contains no GitHub-specific execution logic and no planning
logic. Providers/Bodies populate these contracts; the Brain reasons over them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


VERSION = "2.1-G9-S1"


@dataclass(frozen=True)
class RepositoryIdentity:
    """Stable identity for a repository-like project environment."""

    provider: str
    name: str
    owner: str = ""
    location: str = ""
    repository_id: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.provider).strip():
            raise ValueError("provider is required")
        if not str(self.name).strip():
            raise ValueError("name is required")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "name": self.name,
            "owner": self.owner,
            "location": self.location,
            "repository_id": self.repository_id,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryIdentity":
        if not isinstance(data, dict):
            raise TypeError("repository identity must be a dictionary")

        return cls(
            provider=data.get("provider", ""),
            name=data.get("name", ""),
            owner=data.get("owner", ""),
            location=data.get("location", ""),
            repository_id=data.get("repository_id", ""),
            metadata=data.get("metadata") or {},
        )


@dataclass(frozen=True)
class RepositoryEntry:
    """One file or directory discovered during repository inspection."""

    path: str
    kind: str = "file"
    size: Optional[int] = None
    language: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.path).strip():
            raise ValueError("path is required")

        kind = str(self.kind).strip().lower()
        if kind not in {"file", "directory", "symlink", "other"}:
            raise ValueError(
                "kind must be one of: file, directory, symlink, other"
            )

        if self.size is not None and self.size < 0:
            raise ValueError("size cannot be negative")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "kind": self.kind,
            "size": self.size,
            "language": self.language,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryEntry":
        if not isinstance(data, dict):
            raise TypeError("repository entry must be a dictionary")

        return cls(
            path=data.get("path", ""),
            kind=data.get("kind", "file"),
            size=data.get("size"),
            language=data.get("language", ""),
            metadata=data.get("metadata") or {},
        )


@dataclass(frozen=True)
class RepositoryBranch:
    """Branch/reference information returned by repository inspection."""

    name: str
    is_default: bool = False
    is_current: bool = False
    revision: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValueError("branch name is required")

    def as_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "is_default": self.is_default,
            "is_current": self.is_current,
            "revision": self.revision,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryBranch":
        if not isinstance(data, dict):
            raise TypeError("repository branch must be a dictionary")

        return cls(
            name=data.get("name", ""),
            is_default=bool(data.get("is_default", False)),
            is_current=bool(data.get("is_current", False)),
            revision=data.get("revision", ""),
            metadata=data.get("metadata") or {},
        )


@dataclass
class RepositoryInspection:
    """Snapshot of repository state discovered by a Body."""

    identity: RepositoryIdentity
    default_branch: str = ""
    current_branch: str = ""
    revision: str = ""
    entries: List[RepositoryEntry] = field(default_factory=list)
    branches: List[RepositoryBranch] = field(default_factory=list)
    project_metadata: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = VERSION

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "identity": self.identity.as_dict(),
            "default_branch": self.default_branch,
            "current_branch": self.current_branch,
            "revision": self.revision,
            "entries": [entry.as_dict() for entry in self.entries],
            "branches": [branch.as_dict() for branch in self.branches],
            "project_metadata": dict(self.project_metadata),
            "capabilities": list(self.capabilities),
            "diagnostics": list(self.diagnostics),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepositoryInspection":
        if not isinstance(data, dict):
            raise TypeError("repository inspection must be a dictionary")

        return cls(
            identity=RepositoryIdentity.from_dict(data.get("identity") or {}),
            default_branch=data.get("default_branch", ""),
            current_branch=data.get("current_branch", ""),
            revision=data.get("revision", ""),
            entries=[
                RepositoryEntry.from_dict(item)
                for item in data.get("entries", [])
            ],
            branches=[
                RepositoryBranch.from_dict(item)
                for item in data.get("branches", [])
            ],
            project_metadata=data.get("project_metadata") or {},
            capabilities=list(data.get("capabilities") or []),
            diagnostics=list(data.get("diagnostics") or []),
            metadata=data.get("metadata") or {},
        )

    def files(self) -> List[RepositoryEntry]:
        return [entry for entry in self.entries if entry.kind == "file"]

    def directories(self) -> List[RepositoryEntry]:
        return [entry for entry in self.entries if entry.kind == "directory"]

    def has_capability(self, capability_id: str) -> bool:
        target = str(capability_id or "").strip()
        return target in self.capabilities

    def is_healthy(self) -> bool:
        return not self.diagnostics


__all__ = [
    "VERSION",
    "RepositoryIdentity",
    "RepositoryEntry",
    "RepositoryBranch",
    "RepositoryInspection",
]
