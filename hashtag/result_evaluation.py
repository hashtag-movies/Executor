"""Hashtag Gate 7 Step 2: deterministic result evaluation contract.

This layer evaluates an Observation; it does not execute, route, recover,
re-plan, learn, or modify the operation graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional


VALID_OUTCOMES = {"satisfied", "unsatisfied", "blocked", "uncertain"}


@dataclass
class ResultEvaluation:
    """Structured judgment about whether an observed operation achieved its outcome."""

    node_id: str
    operation: str
    outcome: str
    confidence: float
    reason: str
    evidence: Dict[str, Any] = field(default_factory=dict)
    anomalies: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = "1.9-G7-S2"

    def __post_init__(self):
        self.node_id = str(self.node_id or "").strip()
        self.operation = str(self.operation or "").strip()
        self.outcome = str(self.outcome or "uncertain").strip().lower()
        if self.outcome not in VALID_OUTCOMES:
            raise ValueError(f"Unknown evaluation outcome: {self.outcome}")
        self.confidence = max(0.0, min(1.0, float(self.confidence)))
        self.reason = str(self.reason or "").strip()
        self.evidence = dict(self.evidence or {})
        self.anomalies = [str(x) for x in (self.anomalies or [])]
        self.metadata = dict(self.metadata or {})

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "node_id": self.node_id,
            "operation": self.operation,
            "outcome": self.outcome,
            "confidence": self.confidence,
            "reason": self.reason,
            "evidence": dict(self.evidence),
            "anomalies": list(self.anomalies),
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> Optional["ResultEvaluation"]:
        if data is None:
            return None
        if not isinstance(data, dict):
            raise ValueError("ResultEvaluation must be an object")
        return cls(
            node_id=str(data.get("node_id", "")),
            operation=str(data.get("operation", "")),
            outcome=str(data.get("outcome", "uncertain")),
            confidence=float(data.get("confidence", 0.0)),
            reason=str(data.get("reason", "")),
            evidence=dict(data.get("evidence") or {}),
            anomalies=list(data.get("anomalies") or []),
            metadata=dict(data.get("metadata") or {}),
        )


class ResultEvaluator:
    """Small deterministic evaluator used as the first evaluation layer."""

    VERSION = "1.9-G7-S2"

    def evaluate(self, observation: Any) -> ResultEvaluation:
        status = str(getattr(observation, "status", "unknown") or "unknown").lower()
        node_id = str(getattr(observation, "node_id", "") or "")
        operation = str(getattr(observation, "operation", "") or "")
        output = getattr(observation, "output", None)
        expected = getattr(observation, "expected", None)
        evidence = dict(getattr(observation, "evidence", {}) or {})
        anomalies = list(getattr(observation, "anomalies", []) or [])

        verification = evidence.get("verification")
        if isinstance(verification, dict) and isinstance(verification.get("ok"), bool):
            ok = verification["ok"]
            return ResultEvaluation(
                node_id, operation, "satisfied" if ok else "unsatisfied", 1.0,
                "Explicit verification evidence reports success." if ok else "Explicit verification evidence reports failure.",
                evidence={"verification": verification}, anomalies=anomalies,
                metadata={"method": "explicit_verification"},
            )

        if status == "permission_required":
            return ResultEvaluation(node_id, operation, "blocked", 1.0,
                                    "Execution is blocked pending permission.",
                                    evidence=evidence, anomalies=anomalies,
                                    metadata={"method": "execution_state"})

        if status == "retryable_error":
            return ResultEvaluation(node_id, operation, "blocked", 1.0,
                                    "Execution is blocked by a retryable infrastructure failure.",
                                    evidence=evidence, anomalies=anomalies,
                                    metadata={"method": "execution_state"})

        if status in {"error", "failed"} or "error" in status:
            return ResultEvaluation(node_id, operation, "unsatisfied", 1.0,
                                    "The operation did not execute successfully.",
                                    evidence=evidence, anomalies=anomalies,
                                    metadata={"method": "execution_state"})

        if expected is not None:
            if output == expected:
                return ResultEvaluation(node_id, operation, "satisfied", 0.98,
                                        "Observed output exactly matches the supplied expected value.",
                                        evidence={"expected_match": True}, anomalies=anomalies,
                                        metadata={"method": "exact_expected_match"})
            return ResultEvaluation(node_id, operation, "unsatisfied", 0.98,
                                    "Observed output does not exactly match the supplied expected value.",
                                    evidence={"expected_match": False}, anomalies=anomalies,
                                    metadata={"method": "exact_expected_match"})

        if status == "success" and output is not None:
            return ResultEvaluation(node_id, operation, "uncertain", 0.55,
                                    "Execution succeeded and produced output, but no explicit outcome evidence was supplied.",
                                    evidence=evidence, anomalies=anomalies,
                                    metadata={"method": "successful_execution_without_goal_evidence"})

        return ResultEvaluation(node_id, operation, "uncertain", 0.15,
                                "There is not enough evidence to determine whether the intended outcome was achieved.",
                                evidence=evidence, anomalies=anomalies,
                                metadata={"method": "insufficient_evidence"})
