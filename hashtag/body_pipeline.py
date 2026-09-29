"""
Hashtag V1.7-A
Brain -> normalized Operation -> BodyRouter bridge.

This module deliberately does not create another brain or planner.
It adapts the existing HashtagBrain.plan() result into the existing
V11 normalized Operation contract and routes it through BodyRouter.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .contracts import Operation


class BodyPipelineError(Exception):
    """Base error for the Core Brain -> Body pipeline."""


class PlanNotExecutableError(BodyPipelineError):
    """Raised when the Brain cannot produce an executable operation."""


class HashtagBodyPipeline:
    """
    Thin integration layer between the existing Brain and BodyRouter.

    Architecture:

        request
           |
           v
        HashtagBrain.plan()
           |
           v
        V10 Action(s)
           |
           v
        V11 normalized Operation(s)
           |
           v
        BodyRouter
    """

    def __init__(self, brain, body_router):
        self.brain = brain
        self.body_router = body_router

    def plan(
        self,
        tool: Dict[str, Any],
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ask the existing Brain for its normal V10 plan, then expose
        normalized V11 Operations alongside the legacy actions.

        Existing Brain behavior is not modified.
        """
        result = self.brain.plan(
            tool,
            request,
            context=context or {},
        )

        if not isinstance(result, dict):
            raise PlanNotExecutableError(
                "Hashtag Brain returned an invalid plan."
            )

        actions = result.get("actions") or []
        normalized = []

        for action_data in actions:
            operation = self._action_to_operation(action_data)

            if operation is not None:
                normalized.append(operation.as_dict())

        result = dict(result)
        result["operations"] = normalized
        result["pipeline"] = {
            "version": "1.7-A",
            "source": "hashtag-brain",
            "normalized": bool(normalized),
        }

        return result

    def route(
        self,
        tool: Dict[str, Any],
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Brain-plan the request and route the first normalized operation
        through the existing BodyRouter.

        This is intentionally routing only. It does not execute.
        """
        plan = self.plan(tool, request, context)

        operations = plan.get("operations") or []

        if not operations:
            raise PlanNotExecutableError(
                "Hashtag Brain did not produce a normalized operation "
                "that can be routed to a Body."
            )

        operation = Operation(
            operation=str(operations[0].get("operation", "")),
            arguments=dict(operations[0].get("arguments") or {}),
            reason=str(operations[0].get("reason", "")),
            source=str(operations[0].get("source", "brain")),
            provenance=str(operations[0].get("provenance", "v11")),
            preconditions=list(
                operations[0].get("preconditions") or []
            ),
        )

        routed = self.body_router.route(operation)

        return {
            "ok": True,
            "plan": plan,
            "operation": operation.as_dict(),
            "route": routed,
        }

    @staticmethod
    def _action_to_operation(action_data: Any) -> Optional[Operation]:
        """
        Convert an existing V10 Action into the Gate-1 Operation.

        Supports:
          * dictionaries returned by Brain.plan()
          * Action-like objects exposing to_operation_v11()
        """
        if action_data is None:
            return None

        if hasattr(action_data, "to_operation_v11"):
            return action_data.to_operation_v11()

        if isinstance(action_data, dict):
            capability = str(
                action_data.get("capability", "")
            ).strip()

            if not capability:
                return None

            return Operation.from_action(action_data)

        return None