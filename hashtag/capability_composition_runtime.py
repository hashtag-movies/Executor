"""
Hashtag Gate 8 Step 7
Integration bridge between generic capability composition and the existing
Gate 7 execution / observation / evaluation / recovery / learning runtime.

Architectural rule:
- GoalCapabilityPlanner remains the single planning layer.
- OperationGraph remains the single plan representation.
- OperationGraphExecutor remains the single execution/recovery runtime.
- Existing Observation, ResultEvaluation, Replanner, and RecoveryLearningEngine
  remain authoritative.
- This module only adapts a GoalPlan into that existing runtime and summarizes
  the lifecycle. It does not introduce another executor, planner, or learner.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional

from .goal_capability_planner import GoalCapabilityPlanner, GoalPlan
from .operation_graph import OperationGraph


VERSION = "2.0-G8-S7"


@dataclass
class CompositionExecutionResult:
    goal: str
    plan: GoalPlan
    status: str
    execution: Any = None
    observations: List[Any] = field(default_factory=list)
    evaluations: List[Any] = field(default_factory=list)
    replans_used: int = 0
    learned: bool = False
    diagnostics: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.status in {"success", "completed", "recovered", "ok"}

    def as_dict(self) -> Dict[str, Any]:
        return {
            "goal": self.goal,
            "status": self.status,
            "execution": self.execution,
            "observations": self.observations,
            "evaluations": self.evaluations,
            "replans_used": self.replans_used,
            "learned": self.learned,
            "diagnostics": self.diagnostics,
            "metadata": self.metadata,
        }


class CapabilityCompositionRuntime:
    """
    Thin Gate 8 integration layer.

    `executor_factory` must return the existing Gate 7
    OperationGraphExecutor (or a compatible existing executor). The adapter
    deliberately does not implement execution itself.

    The executor may expose either:
      execute(graph)
    or:
      run(graph)

    If the executor exposes lifecycle collections/results, they are captured
    without changing their ownership.
    """

    VERSION = VERSION

    def __init__(
        self,
        planner: GoalCapabilityPlanner,
        executor_factory: Callable[[], Any],
    ) -> None:
        if planner is None:
            raise ValueError("planner is required")
        if not callable(executor_factory):
            raise ValueError("executor_factory must be callable")
        self.planner = planner
        self.executor_factory = executor_factory

    def plan(
        self,
        goal: str,
        *,
        arguments: Optional[Mapping[str, Any]] = None,
        body_id: Optional[str] = None,
        graph_id: str = "goal_plan",
    ) -> GoalPlan:
        return self.planner.plan(
            goal,
            arguments=arguments,
            body_id=body_id,
            graph_id=graph_id,
        )

    def execute(
        self,
        goal: str,
        *,
        arguments: Optional[Mapping[str, Any]] = None,
        body_id: Optional[str] = None,
        graph_id: str = "goal_plan",
    ) -> CompositionExecutionResult:
        plan = self.plan(
            goal,
            arguments=arguments,
            body_id=body_id,
            graph_id=graph_id,
        )

        if plan.graph is None:
            return CompositionExecutionResult(
                goal=goal,
                plan=plan,
                status="blocked",
                diagnostics=list(plan.diagnostics),
                metadata={
                    "version": self.VERSION,
                    "lifecycle": "plan_blocked",
                },
            )

        executor = self.executor_factory()
        raw = self._execute_with_existing_runtime(executor, plan.graph)

        observations = self._capture(executor, "observations", "observation_log")
        evaluations = self._capture(executor, "evaluations", "evaluation_log")
        replans_used = self._capture_replans(executor, raw)
        learned = self._capture_learned(executor, raw)
        status = self._status(raw)

        return CompositionExecutionResult(
            goal=goal,
            plan=plan,
            status=status,
            execution=raw,
            observations=observations,
            evaluations=evaluations,
            replans_used=replans_used,
            learned=learned,
            diagnostics=list(plan.diagnostics),
            metadata={
                "version": self.VERSION,
                "lifecycle": (
                    "success"
                    if status in {"success", "completed", "recovered", "ok"}
                    else "executed"
                ),
                "single_runtime": True,
                "gate7_recovery_authoritative": True,
                "gate7_learning_authoritative": True,
            },
        )

    @staticmethod
    def _execute_with_existing_runtime(executor: Any, graph: OperationGraph) -> Any:
        execute = getattr(executor, "execute", None)
        if callable(execute):
            return execute(graph)

        run = getattr(executor, "run", None)
        if callable(run):
            return run(graph)

        raise TypeError(
            "executor_factory did not return an existing graph executor "
            "with execute(graph) or run(graph)"
        )

    @staticmethod
    def _capture(executor: Any, *names: str) -> List[Any]:
        for name in names:
            value = getattr(executor, name, None)
            if value is not None:
                if isinstance(value, list):
                    return list(value)
                if isinstance(value, tuple):
                    return list(value)
        return []

    @staticmethod
    def _capture_replans(executor: Any, raw: Any) -> int:
        for source in (executor, raw):
            if isinstance(source, Mapping):
                for key in ("replans_used", "replans", "replan_count"):
                    value = source.get(key)
                    if isinstance(value, int):
                        return value
            else:
                for key in ("replans_used", "replans", "replan_count"):
                    value = getattr(source, key, None)
                    if isinstance(value, int):
                        return value
        return 0

    @staticmethod
    def _capture_learned(executor: Any, raw: Any) -> bool:
        for source in (executor, raw):
            if isinstance(source, Mapping):
                for key in ("learned", "learning", "recovery_learned"):
                    value = source.get(key)
                    if isinstance(value, bool):
                        return value
            else:
                for key in ("learned", "learning", "recovery_learned"):
                    value = getattr(source, key, None)
                    if isinstance(value, bool):
                        return value
        return False

    @staticmethod
    def _status(raw: Any) -> str:
        if isinstance(raw, Mapping):
            for key in ("status", "state", "outcome"):
                value = raw.get(key)
                if value is not None:
                    return str(value).lower()

            # Existing executors may return a structured result with no
            # top-level status. Preserve that as "completed" rather than
            # inventing a failure.
            return "completed"

        for key in ("status", "state", "outcome"):
            value = getattr(raw, key, None)
            if value is not None:
                return str(value).lower()

        return "completed"


__all__ = [
    "CompositionExecutionResult",
    "CapabilityCompositionRuntime",
    "VERSION",
]
