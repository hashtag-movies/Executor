"""
Hashtag V1.7-B
Brain -> normalized Operation -> BodyRouter -> BodyClient execution bridge.

This is a thin orchestration layer.

It does NOT create another brain, planner, memory system, or executor.
The existing HashtagBrain remains the source of planning truth.
The existing BodyRouter remains the source of body selection/routing.
The existing BodyClient remains the transport to the Body.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .body_pipeline import HashtagBodyPipeline, PlanNotExecutableError
from .contracts import Operation


class BodyRequestError(Exception):
    """Base error for the Brain -> Body request pipeline."""


class BodyRequestPipeline:
    """
    V1.7-B request execution pipeline.

    Flow:

        request
           |
           v
        HashtagBrain.plan()
           |
           v
        normalized Operation
           |
           v
        BodyRouter
           |
           v
        BodyClient
           |
           v
        Body execution result
    """

    VERSION = "1.7-B"

    def __init__(self, brain, body_router):
        self.brain = brain
        self.body_router = body_router
        self.pipeline = HashtagBodyPipeline(
            brain=brain,
            body_router=body_router,
        )

    def plan(
        self,
        tool: Dict[str, Any],
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Return the Brain plan plus normalized Operations.

        Existing Brain planning remains authoritative.
        """
        return self.pipeline.plan(
            tool=tool,
            request=request,
            context=context,
        )

    def route(
        self,
        tool: Dict[str, Any],
        request: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Plan and route without executing the Body operation.
        """
        return self.pipeline.route(
            tool=tool,
            request=request,
            context=context,
        )

    def execute(
        self,
        tool: Dict[str, Any],
        request: str,
        context: Optional[Dict[str, Any]] = None,
        *,
        body_id: Optional[str] = None,
        approval_scope: str = "none",
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Plan the request, normalize its operation, route it to a Body,
        and execute it through the existing BodyRouter.

        No new execution engine is created here.
        """

        plan = self.pipeline.plan(
            tool=tool,
            request=request,
            context=context,
        )

        operations = plan.get("operations") or []

        if not operations:
            raise PlanNotExecutableError(
                "Hashtag Brain did not produce a normalized operation "
                "that can be executed by a Body."
            )

        operation_data = operations[0]

        operation = Operation(
            operation=str(
                operation_data.get("operation", "")
            ),
            arguments=dict(
                operation_data.get("arguments") or {}
            ),
            reason=str(
                operation_data.get("reason", "")
            ),
            source=str(
                operation_data.get("source", "brain")
            ),
            provenance=str(
                operation_data.get("provenance", "v11")
            ),
            preconditions=list(
                operation_data.get("preconditions") or []
            ),
        )

        execution = self.body_router.execute(
            operation,
            body_id=body_id,
            task_id=task_id,
            approval_scope=approval_scope,
        )

        return {
            "ok": True,
            "pipeline": {
                "version": self.VERSION,
                "source": "hashtag-brain",
                "body_router": True,
                "executed": True,
            },
            "plan": plan,
            "operation": operation.as_dict(),
            "execution": execution,
        }