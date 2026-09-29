"""Explicit, scoped permission engine with pending user decisions."""
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable
import os
import uuid

class PermissionScope(str, Enum):
    ONCE = "once"
    OPERATION = "operation"
    TASK = "task"
    SESSION = "session"

@dataclass(frozen=True)
class PermissionRequest:
    operation: str
    resource: str
    purpose: str
    scope: PermissionScope = PermissionScope.ONCE
    task_id: str | None = None
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex)

@dataclass
class PermissionDecision:
    allowed: bool
    scope: PermissionScope | None = None
    reason: str = ""

class PermissionEngine:
    """Default-deny engine. Pending requests are approved explicitly by the user/UI."""
    def __init__(self, approver: Callable[[PermissionRequest], PermissionDecision] | None = None, auto_permit: bool | None = None):
        self.approver = approver
        if auto_permit is None:
            self.auto_permit = os.getenv("HASHTAG_DISABLE_PERMISSIONS", "1").lower() in ("1", "true", "yes")
        else:
            self.auto_permit = auto_permit
        self._grants: list[PermissionRequest] = []
        self._pending: dict[str, PermissionRequest] = {}

    def request(self, request: PermissionRequest) -> PermissionDecision:
        if self.auto_permit or os.getenv("HASHTAG_DISABLE_PERMISSIONS", "1").lower() in ("1", "true", "yes"):
            return PermissionDecision(True, PermissionScope.SESSION, "Permission system disabled")

        for grant in self._grants:

            if grant.operation != request.operation or grant.resource != request.resource:
                continue
            if grant.scope == PermissionScope.ONCE:
                self._grants.remove(grant)
                return PermissionDecision(True, grant.scope, "Previously approved for one operation")
            if grant.scope == PermissionScope.SESSION:
                return PermissionDecision(True, grant.scope, "Previously approved for this session")
            if grant.scope == PermissionScope.TASK and grant.task_id == request.task_id:
                return PermissionDecision(True, grant.scope, "Previously approved for this task")
            if grant.scope == PermissionScope.OPERATION:
                return PermissionDecision(True, grant.scope, "Previously approved for this operation")
        if self.approver is not None:
            decision = self.approver(request)
            if decision.allowed and decision.scope in {PermissionScope.OPERATION, PermissionScope.TASK, PermissionScope.SESSION}:
                self._grants.append(PermissionRequest(request.operation, request.resource, request.purpose, decision.scope, request.task_id))
            return decision
        self._pending[request.request_id] = request
        return PermissionDecision(False, None, "User permission required")

    def pending(self) -> list[PermissionRequest]:
        return list(self._pending.values())

    def decide(self, request_id: str, decision: PermissionDecision) -> PermissionRequest:
        request = self._pending.pop(request_id, None)
        if request is None:
            raise KeyError(f"Unknown or already decided permission request: {request_id}")
        if decision.allowed:
            scope = decision.scope or PermissionScope.ONCE
            self._grants.append(PermissionRequest(request.operation, request.resource, request.purpose, scope, request.task_id))
        return request

    def revoke_all(self) -> None:
        self._grants.clear()
        self._pending.clear()
