"""Hashtag Gate 7 Step 1: Observation contract.

This module only defines a structured, serializable observation of what an
operation actually returned. It does not judge correctness, re-plan, retry,
or execute anything.

Gate 7 Step 2 will use these observations for result evaluation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Observation:
    """Normalized observation captured from one executed graph node."""

    node_id: str
    operation: str
    status: str
    output: Any = None
    evidence: Dict[str, Any] = field(default_factory=dict)
    expected: Any = None
    anomalies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = "1.9-G7-S1"

    def __post_init__(self):
        self.node_id = str(self.node_id or "").strip()
        self.operation = str(self.operation or "").strip()
        self.status = str(self.status or "unknown").strip().lower() or "unknown"
        self.evidence = dict(self.evidence or {})
        self.anomalies = [str(item) for item in (self.anomalies or [])]
        self.metadata = dict(self.metadata or {})

    @classmethod
    def from_result(
        cls,
        node_id: str,
        operation: str,
        result: Any,
        *,
        expected: Any = None,
    ) -> "Observation":
        """Capture a Body result without deciding whether it is correct."""
        if isinstance(result, dict):
            status = str(result.get("status") or "unknown")
            output = result.get("result", result.get("output"))

            evidence = {}
            for key in (
                "request_id",
                "task_id",
                "body_id",
                "verification",
                "audit",
            ):
                if key in result:
                    evidence[key] = result[key]

            metadata = {}
            for key in ("message", "error"):
                if key in result:
                    metadata[key] = result[key]
        else:
            status = "unknown"
            output = result
            evidence = {}
            metadata = {}

        return cls(
            node_id=node_id,
            operation=operation,
            status=status,
            output=output,
            evidence=evidence,
            expected=expected,
            anomalies=[],
            metadata=metadata,
        )

    @classmethod
    def from_error(
        cls,
        node_id: str,
        operation: str,
        status: str,
        error: Any,
    ) -> "Observation":
        """Capture an execution exception as an observation."""
        text = str(error or "")
        return cls(
            node_id=node_id,
            operation=operation,
            status=status,
            output=None,
            evidence={"error": text},
            expected=None,
            anomalies=[],
            metadata={},
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "node_id": self.node_id,
            "operation": self.operation,
            "status": self.status,
            "output": self.output,
            "evidence": dict(self.evidence),
            "expected": self.expected,
            "anomalies": list(self.anomalies),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["Observation"]:
        if data is None:
            return None
        if not isinstance(data, dict):
            raise ValueError("Observation must be an object")
        return cls(
            node_id=str(data.get("node_id", "")),
            operation=str(data.get("operation", "")),
            status=str(data.get("status", "unknown")),
            output=data.get("output"),
            evidence=dict(data.get("evidence") or {}),
            expected=data.get("expected"),
            anomalies=list(data.get("anomalies") or []),
            metadata=dict(data.get("metadata") or {}),
        )
