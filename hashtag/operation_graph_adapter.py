"""V1.8 Gate 2: Brain -> OperationGraph compatibility adapter.

This is an adapter only. The existing HashtagBrain remains authoritative for
planning, V10 actions remain supported, and the V1.8 OperationGraph is only a
normalized representation of that existing plan.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .contracts import Operation
from .operation_graph import OperationGraph


class OperationGraphAdapterError(Exception):
    """Base error for the V1.8 Gate 2 adapter."""


class BrainOperationGraphAdapter:
    VERSION = "1.8-G2"

    def __init__(self, brain: Any):
        if brain is None:
            raise OperationGraphAdapterError("brain is required")
        self.brain = brain

    def plan(
        self,
        tool: Dict[str, Any],
        request: str,
        input_text: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run the existing Brain planner, then attach an OperationGraph.

        The current Brain API carries request input through context rather
        than introducing a new input_text planner parameter. We therefore
        preserve the existing API and add inputText to context only when
        supplied.
        """
        planning_context = dict(context or {})

        if input_text != "":
            planning_context.setdefault("inputText", input_text)

        plan = self.brain.plan(
            tool=tool,
            request=request,
            context=planning_context,
        )

        return self.adapt_plan(plan)

    def adapt_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Keep the original plan intact and add its graph representation."""
        if not isinstance(plan, dict):
            raise OperationGraphAdapterError("Brain plan must be a dictionary")

        actions = self._extract_actions(plan)
        operations = self._actions_to_operations(actions)

        graph = OperationGraph.from_operations(
            operations,
            graph_id=str(
                plan.get("request_id")
                or plan.get("task_id")
                or "brain-plan"
            ),
            metadata={
                "source": "brain",
                "adapter": self.VERSION,
                "compatibility": "v10/v11",
            },
        )

        adapted = dict(plan)
        adapted["actions"] = list(actions)
        adapted["operations"] = [operation.as_dict() for operation in operations]
        adapted["operationGraph"] = graph.as_dict()
        adapted["graph"] = graph.as_dict()
        adapted["pipeline"] = self.VERSION
        return adapted

    def graph_from_plan(self, plan: Dict[str, Any]) -> OperationGraph:
        """Reconstruct an OperationGraph from an adapted plan."""
        adapted = self.adapt_plan(plan)
        return OperationGraph.from_dict(adapted["operationGraph"])

    @staticmethod
    def _extract_actions(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = plan.get("actions")

        if actions is None:
            operations = plan.get("operations")
            if isinstance(operations, list):
                return [
                    item.as_dict() if isinstance(item, Operation) else dict(item)
                    for item in operations
                ]
            return []

        if not isinstance(actions, list):
            raise OperationGraphAdapterError("plan.actions must be a list")

        normalized: List[Dict[str, Any]] = []
        for action in actions:
            if isinstance(action, Operation):
                normalized.append(action.as_dict())
            elif isinstance(action, dict):
                normalized.append(dict(action))
            else:
                raise OperationGraphAdapterError(
                    "each plan action must be a dictionary or Operation"
                )
        return normalized

    @staticmethod
    def _actions_to_operations(
        actions: Iterable[Dict[str, Any]],
    ) -> List[Operation]:
        return [Operation.from_action(dict(action)) for action in actions]
