"""Hashtag Gate 7 Step 4: execution-time recovery and replanning.

This is the evolved V1.8 Gate 3 executor.  Gate 7 Step 4 connects the
existing observation/evaluation layers to the Gate 7 Step 3 replanner without
creating a second Brain, BodyRouter, verifier, or recovery runtime.

Execution loop:
    execute -> observe -> evaluate -> recover/replan -> execute alternative

Important compatibility rules:
- successful nodes are never executed again;
- permission_required still pauses the exact graph;
- retryable infrastructure failures still use waiting_retry;
- genuine failures may trigger bounded replanning;
- completed checkpoints remain protected by the existing server/store;
- the replanner is injected, so the central Hashtag Brain or existing
  RecoveryEngine remains the source of candidate operations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from .operation_graph import OperationGraph
from .observation import Observation
from .result_evaluation import ResultEvaluator
from .replanner_G7_step3 import OperationGraphReplanner, ReplanDecision


class OperationGraphExecutionError(Exception):
    """Base error for V1.8 Gate 3 execution."""


class OperationGraphExecutor:
    # Keep the public executor version stable for existing Gate 3 callers.
    VERSION = "1.8-G3"
    GATE7_VERSION = "1.9-G7-S4"

    def __init__(
        self,
        body_router: Any,
        replanner: Optional[OperationGraphReplanner] = None,
        *,
        max_replans: int = 2,
        replan_uncertain: bool = True,
    ):
        if body_router is None:
            raise OperationGraphExecutionError("body_router is required")
        if max_replans < 0:
            raise OperationGraphExecutionError("max_replans must be >= 0")
        if replanner is not None and not isinstance(
            replanner, OperationGraphReplanner
        ):
            raise OperationGraphExecutionError(
                "replanner must be an OperationGraphReplanner or None"
            )

        self.body_router = body_router
        self.evaluator = ResultEvaluator()
        self.replanner = replanner
        self.max_replans = int(max_replans)
        self.replan_uncertain = bool(replan_uncertain)

    @staticmethod
    def _is_retryable_infrastructure_error(error: str) -> bool:
        """Return True for temporary Body/router transport failures."""
        text = str(error or "").lower()
        markers = (
            "could not connect to body",
            "connection refused",
            "actively refused",
            "connection reset",
            "connection aborted",
            "timed out",
            "timeout",
            "temporarily unavailable",
            "service unavailable",
            "body unavailable",
            "failed to reach body",
        )
        return any(marker in text for marker in markers)

    @staticmethod
    def _evaluation_requires_replan(
        evaluation: Any,
        *,
        replan_uncertain: bool,
    ) -> bool:
        if evaluation is None:
            return False

        outcome = str(getattr(evaluation, "outcome", "") or "").lower()
        if outcome == "unsatisfied":
            return True
        if outcome != "uncertain" or not replan_uncertain:
            return False

        # A plain successful Body response with no goal/verifier evidence is
        # intentionally uncertain in Step 2.  Replanning such a result would
        # cause every ordinary successful operation to be retried.  Only
        # genuinely insufficient/ambiguous evidence reaches recovery here.
        method = str(
            (getattr(evaluation, "metadata", {}) or {}).get("method", "")
        )
        return method != "successful_execution_without_goal_evidence"

    def _try_replan(
        self,
        graph: OperationGraph,
        node_id: str,
        *,
        history: List[Dict[str, Any]],
        replanner: Optional[OperationGraphReplanner],
        max_replans: int,
    ) -> Optional[ReplanDecision]:
        """Attempt one bounded graph replacement for a terminal node."""
        if replanner is None:
            return None

        node = graph.get(node_id)
        if node is None or node.evaluation is None:
            return None

        previous_attempt = int(
            (node.metadata or {}).get("replan_attempt") or 0
        )
        attempt = previous_attempt + 1

        if attempt > max_replans:
            history.append(
                {
                    "node_id": node_id,
                    "status": "replan_limit",
                    "replan": False,
                    "attempt": attempt,
                    "max_replans": max_replans,
                    "reason": "The bounded replanning limit was reached.",
                }
            )
            return None

        try:
            decision = self.replanner.replan(
                graph,
                node_id,
                attempt=attempt,
            )
        except Exception as exc:
            history.append(
                {
                    "node_id": node_id,
                    "status": "replan_error",
                    "replan": False,
                    "attempt": attempt,
                    "error": str(exc),
                }
            )
            return None

        history.append(
            {
                "node_id": node_id,
                "status": "replan",
                "replan": bool(decision.replan),
                "attempt": attempt,
                "decision": decision.as_dict(),
            }
        )
        return decision

    def _result_error(self, result: Any, status: str) -> str:
        if isinstance(result, dict):
            return str(
                result.get("error")
                or result.get("message")
                or f"Body execution status: {status or 'unknown'}"
            )
        return "Body execution returned an invalid result"

    def execute(
        self,
        graph: OperationGraph,
        body_id: Optional[str] = None,
        approval_scope: str = "none",
        task_id: Optional[str] = None,
        *,
        replanner: Optional[OperationGraphReplanner] = None,
        max_replans: Optional[int] = None,
        replan_uncertain: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Execute the graph and integrate bounded observation-driven recovery."""
        if not isinstance(graph, OperationGraph):
            raise OperationGraphExecutionError("graph must be an OperationGraph")

        active_replanner = replanner if replanner is not None else self.replanner
        if active_replanner is not None and not isinstance(
            active_replanner, OperationGraphReplanner
        ):
            raise OperationGraphExecutionError(
                "replanner must be an OperationGraphReplanner or None"
            )

        limit = self.max_replans if max_replans is None else int(max_replans)
        if limit < 0:
            raise OperationGraphExecutionError("max_replans must be >= 0")
        uncertain_policy = (
            self.replan_uncertain
            if replan_uncertain is None
            else bool(replan_uncertain)
        )

        history: List[Dict[str, Any]] = []
        replans_used = 0

        # Recompute topological order after every graph replacement.  This is
        # what makes a newly inserted operation executable in the same run.
        while True:
            changed_graph = False
            paused = False

            for ordered_node in graph.topological_order():
                node_id = ordered_node.node_id
                node = graph.get(node_id)
                if node is None:
                    raise OperationGraphExecutionError(
                        f"Graph node disappeared: {node_id}"
                    )

                if node.state in {"success", "superseded"}:
                    continue

                # A waiting node is resumable.  On a subsequent execute/resume
                # call, attempt it again rather than treating the checkpoint
                # state as permanently paused.  The execution branches below
                # will put it back into waiting_permission/waiting_retry if the
                # condition still exists.

                dependency_states = [
                    graph.get(dep).state for dep in node.depends_on
                ]

                if any(state in {"failed", "skipped"} for state in dependency_states):
                    graph.mark_skipped(
                        node_id,
                        reason="A dependency failed or was skipped.",
                    )
                    history.append(
                        {
                            "node_id": node_id,
                            "status": "skipped",
                            "reason": "dependency_failed_or_skipped",
                        }
                    )
                    continue

                if any(state != "success" for state in dependency_states):
                    raise OperationGraphExecutionError(
                        f"Node {node_id} is not ready; dependency states={dependency_states}"
                    )

                graph.mark_running(node_id)

                try:
                    result = self.body_router.execute(
                        node.operation,
                        body_id=body_id,
                        task_id=task_id,
                        approval_scope=approval_scope,
                    )
                except Exception as exc:
                    error = str(exc)

                    if self._is_retryable_infrastructure_error(error):
                        node.observation = Observation.from_error(
                            node_id,
                            node.operation.operation,
                            "retryable_error",
                            error,
                        )
                        node.evaluation = self.evaluator.evaluate(node.observation)
                        graph.mark_waiting_retry(
                            node_id,
                            error=error,
                            reason=(
                                "Retryable Body/infrastructure failure; "
                                "node remains resumable."
                            ),
                            result={
                                "status": "retryable_error",
                                "result": None,
                                "error": error,
                            },
                        )
                        history.append(
                            {
                                "node_id": node_id,
                                "status": "retryable_error",
                                "error": error,
                                "evaluation": (
                                    node.evaluation.as_dict()
                                    if node.evaluation
                                    else None
                                ),
                            }
                        )
                        paused = True
                        break

                    graph.mark_failed(node_id, error=error)
                    node.observation = Observation.from_error(
                        node_id,
                        node.operation.operation,
                        "error",
                        error,
                    )
                    node.evaluation = self.evaluator.evaluate(node.observation)
                    history.append(
                        {
                            "node_id": node_id,
                            "status": "error",
                            "error": error,
                            "evaluation": (
                                node.evaluation.as_dict()
                                if node.evaluation
                                else None
                            ),
                        }
                    )

                    if self._evaluation_requires_replan(
                        node.evaluation,
                        replan_uncertain=uncertain_policy,
                    ) and replans_used < limit:
                        # Temporarily use the call-scoped replanner.
                        decision = self._try_replan(
                            graph,
                            node_id,
                            history=history,
                            replanner=active_replanner,
                            max_replans=limit,
                        )
                        if decision is not None and decision.replan:
                            replans_used += 1
                            changed_graph = True
                            break
                    continue

                status = str(
                    result.get("status", "") if isinstance(result, dict) else ""
                ).strip().lower()

                node.observation = Observation.from_result(
                    node_id,
                    node.operation.operation,
                    result,
                )
                node.evaluation = self.evaluator.evaluate(node.observation)

                if status == "success":
                    graph.mark_success(node_id, result=result)
                    history.append(
                        {
                            "node_id": node_id,
                            "status": "success",
                            "result": result,
                            "evaluation": (
                                node.evaluation.as_dict()
                                if node.evaluation
                                else None
                            ),
                        }
                    )

                    if self._evaluation_requires_replan(
                        node.evaluation,
                        replan_uncertain=uncertain_policy,
                    ) and replans_used < limit:
                        decision = self._try_replan(
                            graph,
                            node_id,
                            history=history,
                            replanner=active_replanner,
                            max_replans=limit,
                        )
                        if decision is not None and decision.replan:
                            replans_used += 1
                            changed_graph = True
                            break

                elif status == "permission_required":
                    reason = (
                        result.get("error")
                        or result.get("message")
                        or "Body permission is required before this operation can continue."
                    )
                    graph.mark_waiting_permission(
                        node_id,
                        result=result,
                        reason=str(reason),
                    )
                    history.append(
                        {
                            "node_id": node_id,
                            "status": "permission_required",
                            "error": str(reason),
                            "result": result,
                            "evaluation": (
                                node.evaluation.as_dict()
                                if node.evaluation
                                else None
                            ),
                        }
                    )
                    paused = True
                    break

                else:
                    error = self._result_error(result, status)
                    graph.mark_failed(node_id, error=error)
                    history.append(
                        {
                            "node_id": node_id,
                            "status": status or "error",
                            "error": error,
                            "result": result,
                            "evaluation": (
                                node.evaluation.as_dict()
                                if node.evaluation
                                else None
                            ),
                        }
                    )

                    if self._evaluation_requires_replan(
                        node.evaluation,
                        replan_uncertain=uncertain_policy,
                    ) and replans_used < limit:
                        decision = self._try_replan(
                            graph,
                            node_id,
                            history=history,
                            replanner=active_replanner,
                            max_replans=limit,
                        )
                        if decision is not None and decision.replan:
                            replans_used += 1
                            changed_graph = True
                            break

            if paused:
                break
            if changed_graph:
                continue
            break

        states = graph.states()
        failed = [
            node_id for node_id, state in states.items() if state == "failed"
        ]
        skipped = [
            node_id for node_id, state in states.items() if state == "skipped"
        ]
        waiting_permission = [
            node_id
            for node_id, state in states.items()
            if state == "waiting_permission"
        ]
        waiting_retry = [
            node_id
            for node_id, state in states.items()
            if state == "waiting_retry"
        ]

        completed = graph.is_complete()
        retryable = bool(waiting_retry)
        permission_required = bool(waiting_permission)
        paused = permission_required or retryable

        return {
            "ok": (
                not failed
                and not skipped
                and not paused
                and completed
            ),
            "paused": paused,
            "permission_required": permission_required,
            "retryable": retryable,
            "completed": completed,
            "recovered": replans_used > 0,
            "replans_used": replans_used,
            "max_replans": limit,
            "pipeline": self.VERSION,
            "gate7": self.GATE7_VERSION,
            "graph": graph.as_dict(),
            "states": states,
            "history": history,
            "failed": failed,
            "skipped": skipped,
            "waiting_permission": waiting_permission,
            "waiting_retry": waiting_retry,
        }
