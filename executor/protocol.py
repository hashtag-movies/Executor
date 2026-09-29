"""Hashtag Body Protocol V1.3.

Transport-neutral contracts for communication between Hashtag Core
and a physical Body.
"""

from dataclasses import dataclass, field
from typing import Any, Literal
import uuid


ApprovalScope = Literal[
    "none",
    "once",
    "operation",
    "task",
    "session",
]


@dataclass(frozen=True)
class Operation:
    """Normalized operation received from Hashtag Core."""

    operation: str
    arguments: dict[str, Any] = field(default_factory=dict)
    request_id: str = field(
        default_factory=lambda: uuid.uuid4().hex
    )
    task_id: str | None = None
    approval_scope: ApprovalScope = "none"
    reason: str = ""
    source: str = "core"

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": "1.1",
            "request_id": self.request_id,
            "task_id": self.task_id,
            "operation": self.operation,
            "arguments": dict(self.arguments),
            "approval_scope": self.approval_scope,
            "reason": self.reason,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            operation=str(data["operation"]),
            arguments=dict(data.get("arguments") or {}),
            request_id=str(
                data.get("request_id") or uuid.uuid4().hex
            ),
            task_id=data.get("task_id"),
            approval_scope=data.get(
                "approval_scope",
                "none",
            ),
            reason=str(data.get("reason") or ""),
            source=str(
                data.get("source") or "core"
            ),
        )


@dataclass
class BodyResult:
    """Structured result returned by a Hashtag Body."""

    request_id: str
    status: str
    result: Any = None
    error: str | None = None
    verification: dict[str, Any] = field(
        default_factory=dict
    )
    audit: dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": "1.1",
            "request_id": self.request_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "verification": self.verification,
            "audit": self.audit,
        }