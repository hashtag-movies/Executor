"""Hashtag Gate 7 Step 3: bounded intelligent replanning contract.

This module does not own the Brain, BodyRouter, executor, verifier, memory,
or recovery engine. It converts evaluation feedback into a safe replacement
operation supplied by an injected candidate generator.

The generator is deliberately injectable: the central Hashtag Brain can become
the source of alternatives without creating a second planner inside this module.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterable, List, Optional

from .contracts import Operation
from .operation_graph import OperationGraph, OperationGraphError, OperationNode
from .result_evaluation import ResultEvaluation


class ReplannerError(ValueError):
    """Base error for bounded replanning."""


@dataclass
class ReplanRequest:
    node_id: str
    original_operation: Dict[str, Any]
    evaluation: Dict[str, Any]
    observation: Optional[Dict[str, Any]] = None
    graph: Dict[str, Any] = field(default_factory=dict)
    attempt: int = 1
    avoid_operations: List[str] = field(default_factory=list)

    VERSION = "1.9-G7-S3"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "node_id": self.node_id,
            "original_operation": dict(self.original_operation),
            "evaluation": dict(self.evaluation),
            "observation": dict(self.observation or {}),
            "graph": dict(self.graph),
            "attempt": self.attempt,
            "avoid_operations": list(self.avoid_operations),
        }


@dataclass
class ReplanDecision:
    ok: bool
    replan: bool
    reason: str
    candidates: List[Operation] = field(default_factory=list)
    selected: Optional[Operation] = None
    replacement_node_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = "1.9-G7-S3"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "ok": self.ok,
            "replan": self.replan,
            "reason": self.reason,
            "candidates": [x.as_dict() for x in self.candidates],
            "selected": self.selected.as_dict() if self.selected else None,
            "replacement_node_id": self.replacement_node_id,
            "metadata": dict(self.metadata),
        }


CandidateGenerator = Callable[[ReplanRequest], Iterable[Any]]


class OperationGraphReplanner:
    """Apply one bounded replacement plan to an OperationGraph."""

    VERSION = "1.9-G7-S3"

    def __init__(
        self,
        candidate_generator: CandidateGenerator,
        *,
        max_candidates: int = 3,
    ):
        if not callable(candidate_generator):
            raise ReplannerError("candidate_generator is required")
        if max_candidates < 1:
            raise ReplannerError("max_candidates must be >= 1")
        self.candidate_generator = candidate_generator
        self.max_candidates = int(max_candidates)

    def build_request(
        self,
        graph: OperationGraph,
        node_id: str,
        *,
        attempt: int = 1,
    ) -> ReplanRequest:
        node = graph.get(node_id)
        if node.evaluation is None:
            raise ReplannerError("node has no result evaluation")

        return ReplanRequest(
            node_id=node.node_id,
            original_operation=node.operation.as_dict(),
            evaluation=node.evaluation.as_dict(),
            observation=(
                node.observation.as_dict() if node.observation is not None else None
            ),
            graph=graph.as_dict(),
            attempt=max(1, int(attempt)),
            avoid_operations=[node.operation.operation],
        )

    def replan(
        self,
        graph: OperationGraph,
        node_id: str,
        *,
        attempt: int = 1,
    ) -> ReplanDecision:
        node = graph.get(node_id)
        evaluation = node.evaluation
        if evaluation is None:
            raise ReplannerError("node has no result evaluation")

        if evaluation.outcome == "blocked":
            return ReplanDecision(
                ok=True,
                replan=False,
                reason="The operation is blocked; infrastructure or permission recovery must handle it.",
                metadata={"method": "blocked_evaluation"},
            )

        if evaluation.outcome not in {"unsatisfied", "uncertain"}:
            return ReplanDecision(
                ok=True,
                replan=False,
                reason="The evaluation does not require a replacement operation.",
                metadata={"method": "evaluation_does_not_require_replan"},
            )

        request = self.build_request(graph, node_id, attempt=attempt)
        generated = self.candidate_generator(request)
        if isinstance(generated, dict):
            if isinstance(generated.get("actions"), list):
                raw_candidates = list(generated["actions"])
            elif isinstance(generated.get("operations"), list):
                raw_candidates = list(generated["operations"])
            else:
                raw_candidates = []
        else:
            raw_candidates = list(generated or [])
        candidates = self._normalize_candidates(raw_candidates)

        original = node.operation
        candidates = [
            candidate
            for candidate in candidates
            if not self._same_operation(candidate, original)
        ][: self.max_candidates]

        if not candidates:
            return ReplanDecision(
                ok=True,
                replan=False,
                reason="No safe alternative operation was supplied by the Brain candidate generator.",
                metadata={"method": "no_alternative_candidate"},
            )

        selected = candidates[0]
        replacement_id = self._replacement_id(graph, node_id, attempt)

        # Preserve the failed/uncertain attempt as history while making the
        # replacement the active path. Downstream dependencies are rewired.
        if node.state not in {"success", "failed", "skipped"}:
            raise ReplannerError(
                f"Node '{node_id}' must be terminal before replanning; state={node.state}"
            )

        graph.mark_superseded(
            node_id,
            reason=f"Replanned after {evaluation.outcome} evaluation.",
        )

        replacement = OperationNode(
            node_id=replacement_id,
            operation=selected,
            depends_on=list(node.depends_on),
            metadata={
                "replan": True,
                "replan_for": node_id,
                "replan_attempt": max(1, int(attempt)),
                "replan_reason": evaluation.reason,
            },
        )
        graph.nodes.append(replacement)

        for downstream in graph.nodes:
            if downstream.node_id in {node_id, replacement_id}:
                continue
            if node_id in downstream.depends_on:
                downstream.depends_on = [
                    replacement_id if dep == node_id else dep
                    for dep in downstream.depends_on
                ]
                # A previous execution may already have skipped this node
                # because the original attempt failed. The replacement path
                # makes it runnable again.
                if downstream.state == "skipped":
                    downstream.state = "pending"
                    downstream.result = None
                    downstream.error = None
                    downstream.observation = None
                    downstream.evaluation = None

        graph._validate()

        return ReplanDecision(
            ok=True,
            replan=True,
            reason="A safe alternative operation was selected and inserted into the graph.",
            candidates=candidates,
            selected=selected,
            replacement_node_id=replacement_id,
            metadata={
                "method": "candidate_generator",
                "attempt": max(1, int(attempt)),
                "replanned_from": node_id,
            },
        )

    @staticmethod
    def _normalize_candidates(raw: Iterable[Any]) -> List[Operation]:
        result: List[Operation] = []
        seen = set()

        for item in raw:
            if isinstance(item, Operation):
                operation = item
            elif isinstance(item, dict):
                if "operation" in item:
                    operation = Operation(
                        operation=str(item.get("operation", "")),
                        arguments=dict(item.get("arguments") or {}),
                        reason=str(item.get("reason", "")),
                        source=str(item.get("source", "brain")),
                        provenance=str(item.get("provenance", "v11")),
                        preconditions=list(item.get("preconditions") or []),
                    )
                elif "capability" in item:
                    operation = Operation.from_action(item)
                else:
                    continue
            else:
                continue

            if not operation.operation:
                continue

            key = (operation.operation, repr(sorted(operation.arguments.items())))
            if key in seen:
                continue
            seen.add(key)
            result.append(operation)

        return result

    @staticmethod
    def _same_operation(left: Operation, right: Operation) -> bool:
        return (
            left.operation == right.operation
            and left.arguments == right.arguments
        )

    @staticmethod
    def _replacement_id(graph: OperationGraph, node_id: str, attempt: int) -> str:
        base = f"{node_id}_replan_{max(1, int(attempt))}"
        candidate = base
        suffix = 2
        while any(node.node_id == candidate for node in graph.nodes):
            candidate = f"{base}_{suffix}"
            suffix += 1
        return candidate
