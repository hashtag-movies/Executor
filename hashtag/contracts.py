from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class Capability:
    id: str
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    def as_dict(self):
        return {"id": self.id, "description": self.description, "input_schema": self.input_schema}

@dataclass
class ToolManifest:
    id: str
    name: str
    version: str
    description: str
    capabilities: List[Capability]
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Action:
    capability: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    source: str = "brain"
    def as_dict(self):
        return {"capability": self.capability, "arguments": self.arguments, "reason": self.reason, "source": self.source}

@dataclass
class Diagnostic:
    level: str
    code: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    def as_dict(self):
        return {"level": self.level, "code": self.code, "message": self.message, "details": self.details}

@dataclass
class SchemaCandidate:
    record_boundary: str = "line"
    delimiter: str = ""
    field_count: int = 0
    fields: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    def as_dict(self):
        return {"record_boundary": self.record_boundary, "delimiter": self.delimiter,
                "field_count": self.field_count, "fields": self.fields,
                "confidence": self.confidence, "evidence": self.evidence}

@dataclass
class Operation:
    operation: str
    arguments: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    source: str = "brain"
    provenance: str = "v11"
    preconditions: List[Dict[str, Any]] = field(default_factory=list)
    def as_dict(self):
        return {"operation": self.operation, "arguments": self.arguments, "reason": self.reason,
                "source": self.source, "provenance": self.provenance, "preconditions": self.preconditions}
    @classmethod
    def from_action(cls, action):
        return cls(str(action.get("capability", "")), dict(action.get("arguments") or {}),
                   str(action.get("reason", "")), str(action.get("source", "brain")), "v10_action")
    def to_v10_action(self):
        if self.provenance not in {"v10_action", "v11_compat"}:
            raise ValueError("Operation is not proven V10-compatible")
        return {"capability": self.operation, "arguments": dict(self.arguments),
                "reason": self.reason, "source": self.source}
