"""Hashtag Gate 7 Step 5: learning from successful recovery.

This layer records only verified, successfully recovered solutions. It reuses the
existing MemoryStore and SkillLearner; it does not create a second memory or brain.
"""
from __future__ import annotations

import time
from typing import Any, Dict, Optional


class RecoveryLearningError(ValueError):
    pass


class RecoveryLearningEngine:
    VERSION = "1.9-G7-S5"

    def __init__(self, memory=None, learner=None):
        self.memory = memory
        self.learner = learner

    @staticmethod
    def _successful_operations(execution: Dict[str, Any]):
        graph = execution.get("graph") or {}
        nodes = graph.get("nodes") or []
        operations = []
        for node in nodes:
            if node.get("state") != "success":
                continue
            op = node.get("operation") or {}
            name = str(op.get("operation") or "").strip()
            if not name:
                continue
            operations.append({
                "capability": name,
                "arguments": dict(op.get("arguments") or {}),
                "reason": str(op.get("reason") or "Recovered operation."),
                "source": str(op.get("source") or "brain"),
            })
        return operations

    @staticmethod
    def _recovered(execution: Dict[str, Any]) -> bool:
        return bool(
            execution.get("ok")
            and execution.get("completed")
            and execution.get("recovered")
            and int(execution.get("replans_used") or 0) > 0
        )

    def learn(
        self,
        *,
        tool_id: Optional[str],
        request: str,
        execution: Dict[str, Any],
        capabilities=None,
        context=None,
    ) -> Dict[str, Any]:
        """Learn a verified recovery without affecting ordinary executions."""
        if not self._recovered(execution):
            return {
                "stored": False,
                "reason": "Execution was not a completed successful recovery.",
                "version": self.VERSION,
            }

        actions = self._successful_operations(execution)
        if not actions:
            return {
                "stored": False,
                "reason": "Recovered execution has no successful active operations to learn.",
                "version": self.VERSION,
            }

        graph = execution.get("graph") or {}
        history = execution.get("history") or []
        replan_events = [x for x in history if x.get("status") == "replan" and x.get("replan")]
        evidence = {
            "replans_used": int(execution.get("replans_used") or 0),
            "replan_events": replan_events[-5:],
            "successful_operations": actions,
            "pipeline": execution.get("pipeline"),
            "gate7": execution.get("gate7"),
        }

        stored_skill = None
        if self.learner is not None:
            plan = {"actions": actions, "request": request}
            verification = {
                "ok": True,
                "confidence": 0.95,
                "errors": [],
                "warnings": [],
                "evidence": [
                    "Execution completed successfully after replanning.",
                    f"{execution.get('replans_used', 0)} bounded replan(s) were used.",
                ],
            }
            try:
                stored_skill = self.learner.learn_from_success(
                    tool_id, request, plan, verification, capabilities=capabilities
                )
            except Exception:
                stored_skill = None

        solution = {
            "kind": "successful_solution",
            "scope": "shared",
            "tool_id": tool_id,
            "intent": (request or "").strip()[:240],
            "request_example": (request or "")[:240],
            "operations": actions,
            "replans_used": int(execution.get("replans_used") or 0),
            "confidence": 0.95,
            "evidence": evidence,
            "skill_learned": bool(stored_skill),
            "learned_at": time.time(),
            "context": dict(context or {}),
        }

        if self.memory is not None:
            try:
                self.memory.learn(solution)
            except Exception:
                return {
                    "stored": False,
                    "skill_learned": bool(stored_skill),
                    "reason": "Recovery was verified but persistent memory storage failed.",
                    "version": self.VERSION,
                }

        return {
            "stored": True,
            "skill_learned": bool(stored_skill),
            "solution": solution,
            "version": self.VERSION,
        }
