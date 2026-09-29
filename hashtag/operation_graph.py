"""
Hashtag V1.8 Gate 1
Operation Graph contract.

This module is contract-only. It does not execute operations, route Bodies,
call the verifier, or alter the existing V1.7 execution pipeline.

Purpose:
    Represent a multi-step plan as a dependency-aware graph while preserving
    the existing V10/V11 Operation contract.

Execution is deliberately out of scope for Gate 1.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional

from .contracts import Operation
from .observation import Observation
from .result_evaluation import ResultEvaluation


class OperationGraphError(ValueError):
    """Base error for invalid Operation Graph contracts."""


class OperationGraphStateError(OperationGraphError):
    """Raised when a graph state transition is invalid."""


VALID_STATES = {
    "pending",
    "ready",
    "running",
    "waiting_permission",
    "waiting_retry",
    "success",
    "failed",
    "skipped",
    "superseded",
}


@dataclass
class OperationNode:
    """
    One node in the V1.8 operation graph.

    `operation` is the existing normalized Hashtag Operation.
    `depends_on` contains node IDs that must complete successfully first.
    """

    node_id: str
    operation: Operation
    depends_on: List[str] = field(default_factory=list)
    state: str = "pending"
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    observation: Optional[Observation] = None
    evaluation: Optional[ResultEvaluation] = None

    def __post_init__(self):
        self.node_id = str(self.node_id or "").strip()
        if not self.node_id:
            raise OperationGraphError("node_id is required")

        if self.state not in VALID_STATES:
            raise OperationGraphStateError(
                f"Unknown operation node state: {self.state}"
            )

        self.depends_on = [
            str(value).strip()
            for value in (self.depends_on or [])
            if str(value).strip()
        ]

        if self.node_id in self.depends_on:
            raise OperationGraphError(
                f"Node '{self.node_id}' cannot depend on itself"
            )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationNode":
        if not isinstance(data, dict):
            raise OperationGraphError("Operation node must be an object")

        raw_operation = data.get("operation")

        if isinstance(raw_operation, Operation):
            operation = raw_operation
        elif isinstance(raw_operation, dict):
            operation = Operation(
                operation=str(raw_operation.get("operation", "")),
                arguments=dict(raw_operation.get("arguments") or {}),
                reason=str(raw_operation.get("reason", "")),
                source=str(raw_operation.get("source", "brain")),
                provenance=str(raw_operation.get("provenance", "v11")),
                preconditions=list(raw_operation.get("preconditions") or []),
            )
        elif "capability" in data:
            # Compatibility convenience for existing V10 actions.
            operation = Operation.from_action(data)
        else:
            raise OperationGraphError(
                "Operation node requires an 'operation' object"
            )

        return cls(
            node_id=str(data.get("node_id", "")),
            operation=operation,
            depends_on=list(data.get("depends_on") or []),
            state=str(data.get("state", "pending")),
            result=data.get("result"),
            error=data.get("error"),
            metadata=dict(data.get("metadata") or {}),
            observation=Observation.from_dict(data.get("observation")),
            evaluation=ResultEvaluation.from_dict(data.get("evaluation")),
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "operation": self.operation.as_dict(),
            "depends_on": list(self.depends_on),
            "state": self.state,
            "result": self.result,
            "error": self.error,
            "metadata": dict(self.metadata),
            "observation": (
                self.observation.as_dict() if self.observation is not None else None
            ),
            "evaluation": (
                self.evaluation.as_dict() if self.evaluation is not None else None
            ),
        }


@dataclass
class OperationGraph:
    """
    Dependency-aware collection of normalized Hashtag operations.

    Gate 1 responsibilities:
      - stable graph representation
      - operation preservation
      - dependency validation
      - deterministic topological ordering
      - readiness calculation
      - explicit state/result/error storage
      - lossless serialization

    Gate 1 deliberately does NOT:
      - execute operations
      - select Bodies
      - request permissions
      - verify results
      - recover/re-plan
      - learn
    """

    graph_id: str = "graph"
    nodes: List[OperationNode] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    VERSION = "1.8-G1"

    def __post_init__(self):
        self.graph_id = str(self.graph_id or "").strip() or "graph"
        self.nodes = list(self.nodes or [])
        self._validate()

    @classmethod
    def from_operations(
        cls,
        operations: Iterable[Operation | Dict[str, Any]],
        *,
        graph_id: str = "graph",
        dependencies: Optional[Iterable[Iterable[str]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "OperationGraph":
        raw_operations = list(operations or [])
        dependency_rows = list(dependencies or [])

        nodes: List[OperationNode] = []

        for index, raw in enumerate(raw_operations, start=1):
            if isinstance(raw, Operation):
                operation = raw
            elif isinstance(raw, dict):
                if "operation" in raw:
                    operation = Operation(
                        operation=str(raw.get("operation", "")),
                        arguments=dict(raw.get("arguments") or {}),
                        reason=str(raw.get("reason", "")),
                        source=str(raw.get("source", "brain")),
                        provenance=str(raw.get("provenance", "v11")),
                        preconditions=list(raw.get("preconditions") or []),
                    )
                else:
                    operation = Operation.from_action(raw)
            else:
                raise OperationGraphError(
                    "from_operations accepts Operation objects or dictionaries"
                )

            node_id = f"op_{index}"

            if index <= len(dependency_rows):
                depends_on = list(dependency_rows[index - 1] or [])
            else:
                # Default linear graph: each later operation depends on the
                # immediately preceding operation.
                depends_on = [f"op_{index - 1}"] if index > 1 else []

            nodes.append(
                OperationNode(
                    node_id=node_id,
                    operation=operation,
                    depends_on=depends_on,
                )
            )

        return cls(
            graph_id=graph_id,
            nodes=nodes,
            metadata=dict(metadata or {}),
        )

    def _validate(self) -> None:
        ids = [node.node_id for node in self.nodes]

        if len(ids) != len(set(ids)):
            raise OperationGraphError("Operation node IDs must be unique")

        known = set(ids)

        for node in self.nodes:
            if not node.operation.operation:
                raise OperationGraphError(
                    f"Node '{node.node_id}' has an empty operation"
                )

            missing = [dep for dep in node.depends_on if dep not in known]
            if missing:
                raise OperationGraphError(
                    f"Node '{node.node_id}' has unknown dependencies: {missing}"
                )

        # Cycle detection.
        visiting = set()
        visited = set()

        def visit(node_id: str):
            if node_id in visiting:
                raise OperationGraphError(
                    f"Operation graph contains a dependency cycle at '{node_id}'"
                )
            if node_id in visited:
                return

            visiting.add(node_id)
            node = self.get(node_id)
            for dep in node.depends_on:
                visit(dep)
            visiting.remove(node_id)
            visited.add(node_id)

        for node_id in ids:
            visit(node_id)

    def get(self, node_id: str) -> OperationNode:
        target = str(node_id or "").strip()
        for node in self.nodes:
            if node.node_id == target:
                return node
        raise OperationGraphError(f"Unknown operation node: {target}")

    def operation(self, node_id: str) -> Operation:
        return self.get(node_id).operation

    def ready_nodes(self) -> List[OperationNode]:
        """
        Return pending/ready nodes whose dependencies all succeeded.

        Failed/skipped dependencies prevent a node from becoming ready.
        """

        result = []

        for node in self.nodes:
            if node.state not in {"pending", "ready"}:
                continue

            dependencies = [self.get(dep) for dep in node.depends_on]

            if all(dep.state == "success" for dep in dependencies):
                if node.state == "pending":
                    node.state = "ready"
                result.append(node)

        return result

    def mark_running(self, node_id: str) -> OperationNode:
        node = self.get(node_id)

        if node.state not in {"pending", "ready", "waiting_permission", "waiting_retry"}:
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot start from state '{node.state}'"
            )

        dependencies = [self.get(dep) for dep in node.depends_on]
        if not all(dep.state == "success" for dep in dependencies):
            raise OperationGraphStateError(
                f"Node '{node_id}' is not ready; dependencies are incomplete"
            )

        node.state = "running"
        node.error = None
        return node

    def mark_waiting_permission(
        self,
        node_id: str,
        result: Any = None,
        reason: str = "",
    ) -> OperationNode:
        """Pause a running node while preserving it for checkpoint/resume."""
        node = self.get(node_id)

        if node.state != "running":
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot wait for permission from state '{node.state}'"
            )

        node.state = "waiting_permission"
        node.result = result
        node.error = str(reason or "") or None
        return node

    def mark_waiting_retry(
        self,
        node_id: str,
        error: Any = None,
        reason: str = "",
        result: Any = None,
    ) -> OperationNode:
        """Pause a running node after a retryable infrastructure/body failure."""
        node = self.get(node_id)

        if node.state != "running":
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot wait for retry from state '{node.state}'"
            )

        node.state = "waiting_retry"
        node.result = result
        node.error = str(error or reason or "") or None
        if reason:
            node.metadata["retry_reason"] = str(reason)
        return node

    def mark_success(
        self,
        node_id: str,
        result: Any = None,
    ) -> OperationNode:
        node = self.get(node_id)

        if node.state != "running":
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot succeed from state '{node.state}'"
            )

        node.state = "success"
        node.result = result
        node.error = None
        return node

    def mark_failed(
        self,
        node_id: str,
        error: Any,
    ) -> OperationNode:
        node = self.get(node_id)

        if node.state != "running":
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot fail from state '{node.state}'"
            )

        node.state = "failed"
        node.error = str(error)
        return node

    def mark_superseded(
        self,
        node_id: str,
        reason: str = "",
    ) -> OperationNode:
        """Retire a node because a replanned replacement will take its place."""
        node = self.get(node_id)

        if node.state not in {"success", "failed", "skipped"}:
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot be superseded from state '{node.state}'"
            )

        node.state = "superseded"
        node.error = str(reason or "") or None
        node.metadata["superseded"] = True
        return node

    def mark_skipped(
        self,
        node_id: str,
        reason: str = "",
    ) -> OperationNode:
        node = self.get(node_id)

        if node.state in {"success", "failed"}:
            raise OperationGraphStateError(
                f"Node '{node_id}' cannot be skipped from state '{node.state}'"
            )

        node.state = "skipped"
        node.error = str(reason or "") or None
        return node

    def topological_order(self) -> List[OperationNode]:
        """
        Return nodes in deterministic dependency order.

        Original insertion order is used as the tie-breaker for independent
        nodes so graph serialization and tests remain deterministic.
        """

        ordered: List[OperationNode] = []
        remaining = list(self.nodes)
        completed = set()

        while remaining:
            progress = False

            for node in list(remaining):
                if all(dep in completed for dep in node.depends_on):
                    ordered.append(node)
                    completed.add(node.node_id)
                    remaining.remove(node)
                    progress = True

            if not progress:
                raise OperationGraphError(
                    "Unable to topologically order operation graph"
                )

        return ordered

    def states(self) -> Dict[str, str]:
        return {node.node_id: node.state for node in self.nodes}

    def is_complete(self) -> bool:
        return all(
            node.state in {"success", "failed", "skipped", "superseded"}
            for node in self.nodes
        )

    def succeeded(self) -> bool:
        return bool(self.nodes) and all(
            node.state == "success" for node in self.nodes
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "version": self.VERSION,
            "graph_id": self.graph_id,
            "nodes": [node.as_dict() for node in self.nodes],
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OperationGraph":
        if not isinstance(data, dict):
            raise OperationGraphError("Operation graph must be an object")

        return cls(
            graph_id=str(data.get("graph_id", "graph")),
            nodes=[
                OperationNode.from_dict(item)
                for item in (data.get("nodes") or [])
            ],
            metadata=dict(data.get("metadata") or {}),
        )
