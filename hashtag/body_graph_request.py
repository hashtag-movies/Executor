"""V1.8 Gate 4: request-level OperationGraph integration adapter.

This module is deliberately separate from server.py for the first Gate 4
implementation. It composes the already-existing:
- BrainOperationGraphAdapter
- OperationGraphExecutor
- BodyRouter

It does not create a new planner or execution runtime.

The adapter supports a conservative compatibility rule:
- a one-operation graph is executed through the graph executor as well, so the
  graph path has one authoritative execution mechanism;
- the returned structure keeps the original plan and adds graph/execution
  information;
- verification/recovery are not changed in Gate 4A.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .operation_graph_adapter import (
    BrainOperationGraphAdapter,
    OperationGraphAdapterError,
)
from .operation_graph_executor import (
    OperationGraphExecutionError,
    OperationGraphExecutor,
)


class BodyGraphRequestError(Exception):
    """Base error for V1.8 Gate 4 request integration."""


class BodyGraphRequestPipeline:
    """Plan a request into a graph and execute that graph through BodyRouter."""

    VERSION = "1.8-G4"

    def __init__(self, brain: Any, body_router: Any):
        if brain is None:
            raise BodyGraphRequestError("brain is required")
        if body_router is None:
            raise BodyGraphRequestError("body_router is required")

        self.brain = brain
        self.body_router = body_router
        self.graph_adapter = BrainOperationGraphAdapter(brain)
        self.graph_executor = OperationGraphExecutor(body_router)

    def plan(
        self,
        tool: Dict[str, Any],
        request: str,
        input_text: str = "",
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return self.graph_adapter.plan(
            tool=tool,
            request=request,
            input_text=input_text,
            context=context,
        )

    def execute(
        self,
        tool: Dict[str, Any],
        request: str,
        input_text: str = "",
        context: Optional[Dict[str, Any]] = None,
        body_id: Optional[str] = None,
        approval_scope: str = "none",
        task_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        plan = self.plan(
            tool=tool,
            request=request,
            input_text=input_text,
            context=context,
        )

        graph = self.graph_adapter.graph_from_plan(plan)

        if not graph.nodes:
            return {
                "ok": False,
                "pipeline": self.VERSION,
                "plan": plan,
                "operationGraph": graph.as_dict(),
                "execution": {
                    "ok": False,
                    "pipeline": OperationGraphExecutor.VERSION,
                    "graph": graph.as_dict(),
                    "states": {},
                    "history": [],
                    "failed": [],
                    "skipped": [],
                },
                "message": "Hashtag produced no executable operations.",
            }

        execution = self.graph_executor.execute(
            graph,
            body_id=body_id,
            approval_scope=approval_scope,
            task_id=task_id,
        )

        return {
            "ok": bool(execution.get("ok")),
            "pipeline": self.VERSION,
            "plan": plan,
            "operationGraph": execution.get("graph"),
            "execution": execution,
            "message": (
                "OperationGraph execution completed successfully."
                if execution.get("ok")
                else "OperationGraph execution did not complete successfully."
            ),
        }
