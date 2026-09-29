"""
Hashtag V1.7-C
Brain -> Body execution -> Verification -> bounded Recovery.

This module only orchestrates the existing Hashtag components.

It does NOT create:
- another Brain
- another Verifier
- another RecoveryEngine
- another MemoryStore
- another execution engine

Existing components remain authoritative.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .body_request import BodyRequestPipeline
from .contracts import Operation
from .goal_capability_planner import GoalCapabilityPlanner


class BodyRecoveryError(Exception):
    """Base error for the verified Body execution pipeline."""


class BodyRecoveryPipeline:
    """
    V1.7-C verified execution pipeline.

    Flow:

        Brain
          â†“
        Operation
          â†“
        BodyRouter
          â†“
        BodyClient
          â†“
        Body
          â†“
        Existing HashtagVerifier
          â†“
        Existing RecoveryEngine
          â†“
        retry
          â†“
        verify again
    """

    VERSION = "1.8-G9-S8"

    def __init__(self, brain, body_router, verifier, recovery):
        self.brain = brain
        self.body_router = body_router
        self.verifier = verifier
        self.recovery = recovery

        self.request_pipeline = BodyRequestPipeline(
            brain=brain,
            body_router=body_router,
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
        input_text: str = "",
        max_replans: Optional[int] = None,
        max_steps: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Execute the Brain's plan through a Body and verify the result.

        If verification fails, use the existing RecoveryEngine to produce
        a bounded alternative plan and retry.

        The input text is passed to the verifier/recovery system as the
        original source text. The Body itself receives the operation's
        arguments exactly as planned by the Brain.
        """

        plan = self.request_pipeline.plan(
            tool=tool,
            request=request,
            context=context,
        )

        operations = plan.get("operations") or []

        if not operations:
            # A semantic provider may claim completion, but Core must prove
            # that claim from observable execution evidence.
            if plan.get("provider_goal_complete"):
                evidence = self._completion_evidence(request, history=[], context=context)
                if evidence["ok"]:
                    return {
                        "ok": True,
                        "pipeline": {
                            "version": self._pipeline_version(working_plan),
                            "verified": True,
                            "goal_complete": True,
                            "steps": 0,
                        },
                        "plan": plan,
                        "operation": {},
                        "execution": {},
                        "verification": {"ok": True, "errors": [], "warnings": []},
                        "completion_evidence": evidence,
                        "history": [],
                    }
                raise BodyRecoveryError(
                    "Hashtag Brain claimed goal completion, but Core could not prove the goal: "
                    + "; ".join(evidence["missing"])
                )
            raise BodyRecoveryError(
                "Hashtag Brain did not produce a normalized operation."
            )

        working_plan = dict(plan)
        before = str(input_text or "")

        attempt = int(working_plan.get("attempt", 1) or 1)

        if max_replans is None:
            max_replans = max(8, int(getattr(self.recovery, "MAX_REPLANS", 2)))
        max_replans = max(0, max_replans)

        if max_steps is None:
            # Continuation is bounded separately from failure recovery. This
            # prevents a semantic model loop from becoming unbounded while
            # preserving the existing RecoveryEngine retry budget.
            max_steps = max(40, max_replans + 20)
        max_steps = max(1, int(max_steps))


        context = dict(context or {})
        history = list(context.get("history") or [])
        observations = list(context.get("observations") or [])
        completed_operations = list(context.get("completed_operations") or [])
        step = int(context.get("step") or len(observations) or 0)
        recovery_attempts = int(context.get("recovery_attempts") or 0)

        while True:
            if step >= max_steps:
                return {
                    "ok": False,
                    "pipeline": {
                        "version": self._pipeline_version(working_plan),
                        "verified": False,
                        "goal_complete": False,
                        "steps": step,
                        "max_steps": max_steps,
                        "recovered": recovery_attempts > 0,
                    },
                    "plan": working_plan,
                    "operation": self._first_operation(working_plan),
                    "execution": history[-1]["execution"] if history else {},
                    "verification": history[-1]["verification"] if history else {},
                    "history": history,
                    "message": "Semantic goal continuation reached its bounded step limit before the goal was verified.",
                }

            step += 1

            execution = self._execute_plan(
                working_plan,
                body_id=body_id,
                task_id=task_id,
                approval_scope=approval_scope,
            )

            verification_execution = self._verification_execution(
                execution,
                before,
            )

            verification = self.verifier.verify(
                working_plan,
                verification_execution,
            )

            operation = self._first_operation(working_plan)
            output = self._output_text(execution)
            history_item = {
                "step": step,
                "attempt": attempt,
                "operation": operation,
                "execution": execution,
                "verification": verification,
            }
            history.append(history_item)

            execution_status = str(execution.get("status", "") or "").strip().lower()

            # Permission is a user-authorization state, not a planning
            # failure. Never try to bypass it by semantic replanning.
            if execution_status == "permission_required":
                continuation_context = dict(context or {})
                continuation_context.update({
                    "goal": request,
                    "original_request": request,
                    "observations": observations[-8:],
                    "completed_operations": completed_operations[-8:],
                    "history": history[-8:],
                    "last_operation": operation,
                    "last_execution": execution,
                    "last_verification": verification,
                    "step": len(completed_operations),
                    "max_steps": max_steps,
                    "recovery_attempts": recovery_attempts,
                })
                return {
                    "ok": False,
                    "paused": True,
                    "permission_required": True,
                    "pipeline": {
                        "version": self._pipeline_version(working_plan),
                        "verified": False,
                        "goal_complete": False,
                        "recovered": recovery_attempts > 0,
                        "attempt": attempt,
                        "steps": step,
                        "paused": True,
                        "permission_required": True,
                    },
                    "plan": working_plan,
                    "operation": operation,
                    "execution": execution,
                    "verification": verification,
                    "history": history,
                    "observations": observations,
                    "completed_operations": completed_operations,
                    "context": continuation_context,
                    "message": (
                        "Hashtag understood the request, but the Executor requires "
                        "user permission before this operation can continue."
                    ),
                }

            if not verification.get("ok"):
                if recovery_attempts >= max_replans:
                    return {
                        "ok": False,
                        "pipeline": {
                            "version": self._pipeline_version(working_plan),
                            "verified": False,
                            "goal_complete": False,
                            "recovered": recovery_attempts > 0,
                            "attempt": attempt,
                            "max_replans": max_replans,
                            "steps": step,
                        },
                        "plan": working_plan,
                        "operation": operation,
                        "execution": execution,
                        "verification": verification,
                        "history": history,
                        "message": "Verification failed and the bounded recovery limit was reached.",
                    }

                alternative = self.recovery.replan(
                    working_plan,
                    verification,
                    before,
                    output,
                )

                if not alternative:
                    semantic_plan = bool(working_plan.get("provider_used")) or any(
                        isinstance(action, dict) and str(
                            action.get("source", "")
                        ).lower() == "provider"
                        for action in (working_plan.get("actions") or [])
                    ) or any(
                        isinstance(op, dict) and str(
                            op.get("source", "")
                        ).lower() == "provider"
                        for op in (working_plan.get("operations") or [])
                    )
                    operation_name = str(operation.get("operation", "")).strip()
                    repository_semantic = operation_name.startswith("repository.")

                    if (semantic_plan or repository_semantic) and recovery_attempts < max_replans:
                        recovery_attempts += 1
                        completed_operations.append(operation)
                        observations.append({
                            "step": step,
                            "operation": operation,
                            "status": "error",
                            "output": str(execution.get("error") or output)[:12000],
                            "verification": verification,
                        })
                    else:
                        return {
                            "ok": False,
                            "pipeline": {
                                "version": self._pipeline_version(working_plan),
                                "verified": False,
                                "goal_complete": False,
                                "recovered": recovery_attempts > 0,
                                "attempt": attempt,
                                "max_replans": max_replans,
                                "steps": step,
                            },
                            "plan": working_plan,
                            "operation": operation,
                            "execution": execution,
                            "verification": verification,
                            "history": history,
                            "message": "Verification failed, but Hashtag could not find a safe alternative plan.",
                        }
                else:
                    new_plan = dict(working_plan)
                    new_plan["actions"] = list(alternative.get("actions") or [])
                    recovery_attempts += 1
                    attempt += 1
                    new_plan["attempt"] = attempt
                    new_plan["mode"] = "recovery"
                    new_plan["recoveryReason"] = alternative.get("reason", "")
                    new_plan["operations"] = self._actions_to_operations(new_plan["actions"])
                    working_plan = new_plan
                    continue
            else:
                # The operation succeeded. Record the observation as evidence for
                # the next semantic planning turn. The Brain remains the only
                # planner; this pipeline only supplies execution evidence.
                completed_operations.append(operation)
                observations.append({
                    "step": step,
                    "operation": operation,
                    "status": execution_status or "success",
                    "output": output[:12000],
                    "verification": verification,
                })

            # Preserve the original V1.7 single-operation contract. A
            # deterministic/legacy plan that has already executed and passed
            # verification may complete immediately when its observable goal
            # evidence is sufficient. Semantic provider plans remain under
            # provider-directed continuation unless the provider explicitly
            # declares completion.
            semantic_plan = bool(working_plan.get("provider_used")) or any(
                isinstance(action, dict) and str(
                    action.get("source", "")
                ).lower() == "provider"
                for action in (working_plan.get("actions") or [])
            ) or any(
                isinstance(op, dict) and str(
                    op.get("source", "")
                ).lower() == "provider"
                for op in (working_plan.get("operations") or [])
            )
            operation_name = str(operation.get("operation", "")).strip()
            repository_semantic = operation_name.startswith("repository.")
            if (
                not semantic_plan
                and not repository_semantic
                and not bool(working_plan.get("provider_goal_complete"))
            ):
                legacy_evidence = self._completion_evidence(
                    request, history=history, context=context
                )
                if legacy_evidence["ok"]:
                    return {
                        "ok": True,
                        "pipeline": {
                            "version": self._pipeline_version(working_plan),
                            "verified": True,
                            "goal_complete": True,
                            "recovered": recovery_attempts > 0,
                            "attempt": attempt,
                            "steps": step,
                        },
                        "plan": working_plan,
                        "operation": operation,
                        "execution": execution,
                        "verification": verification,
                        "completion_evidence": legacy_evidence,
                        "history": history,
                    }

            # A provider completion claim is advisory. Core accepts it when
            # the observable execution history proves the goal.
            # Also, if the user requested a modification and it succeeded without
            # requiring further tests/reads, complete immediately.
            evidence = self._completion_evidence(request, history=history, context=context)
            if evidence["ok"] and (
                bool(working_plan.get("provider_goal_complete"))
                or (evidence.get("wants_change") and not evidence.get("wants_run") and not evidence.get("wants_read") and not evidence.get("wants_list"))
            ):
                return {
                    "ok": True,
                    "pipeline": {
                        "version": self._pipeline_version(working_plan),
                        "verified": True,
                        "goal_complete": True,
                        "recovered": recovery_attempts > 0,
                        "attempt": attempt,
                        "steps": step,
                    },
                    "plan": working_plan,
                    "operation": operation,
                    "execution": execution,
                    "verification": verification,
                    "completion_evidence": evidence,
                    "history": history,
                }

            continuation_context = dict(context or {})
            continuation_context.update({
                "goal": request,
                "original_request": request,
                "observations": observations[-8:],
                "completed_operations": completed_operations[-8:],
                "last_operation": operation,
                "last_execution": execution,
                "last_verification": verification,
                "step": step,
                "max_steps": max_steps,
            })

            print("\n[G9-S8 DEBUG] ===== CONTINUATION =====")
            print("[G9-S8 DEBUG] step:", step)
            print("[G9-S8 DEBUG] tool_id:", tool.get("id") if isinstance(tool, dict) else type(tool).__name__)
            print("[G9-S8 DEBUG] capability_count:", len(tool.get("capabilities") or []) if isinstance(tool, dict) else -1)
            print("[G9-S8 DEBUG] capabilities:", tool.get("capabilities") if isinstance(tool, dict) else None)
            print("[G9-S8 DEBUG] context_keys:", sorted(continuation_context.keys()))
            print("[G9-S8 DEBUG] observation_count:", len(continuation_context.get("observations") or []))
            print("[G9-S8 DEBUG] completed_count:", len(continuation_context.get("completed_operations") or []))
            print("[G9-S8 DEBUG] last_operation:", continuation_context.get("last_operation"))
            print("[G9-S8 DEBUG] last_execution_status:", (continuation_context.get("last_execution") or {}).get("status") if isinstance(continuation_context.get("last_execution"), dict) else None)
            print("[G9-S8 DEBUG] last_verification:", continuation_context.get("last_verification"))

            next_plan = self.request_pipeline.plan(
                tool=tool,
                request=request,
                context=continuation_context,
            )

            print("[G9-S8 DEBUG] next_plan:", next_plan)
            print("[G9-S8 DEBUG] ===== END CONTINUATION =====\n")

            next_operations = next_plan.get("operations") or []

            if next_plan.get("provider_goal_complete"):
                evidence = self._completion_evidence(request, history=history, context=continuation_context)
                if evidence["ok"]:
                    return {
                        "ok": True,
                        "pipeline": {
                            "version": self._pipeline_version(working_plan),
                            "verified": True,
                            "goal_complete": True,
                            "recovered": recovery_attempts > 0,
                            "attempt": attempt,
                            "steps": step,
                        },
                        "plan": next_plan,
                        "operation": operation,
                        "execution": execution,
                        "verification": verification,
                        "completion_evidence": evidence,
                        "history": history,
                    }
                next_plan = dict(next_plan)
                next_plan["provider_goal_complete"] = False

            if not next_operations:
                if next_plan.get("provider_goal_complete") is False:
                    # Provider claimed goal completion early. Prompt for remaining work.
                    continuation_context["observations"].append({
                        "step": step,
                        "operation": {"operation": "goal_verification"},
                        "status": "tests_still_failing",
                        "output": "Tests are still failing! Fix the remaining defective files before declaring goal complete.",
                    })
                    next_plan = self.request_pipeline.plan(
                        tool=tool,
                        request=request,
                        context=continuation_context,
                    )
                    next_operations = next_plan.get("operations") or []

            if not next_operations:
                return {
                    "ok": False,
                    "pipeline": {
                        "version": self._pipeline_version(working_plan),
                        "verified": False,
                        "goal_complete": False,
                        "recovered": recovery_attempts > 0,
                        "attempt": attempt,
                        "steps": step,
                    },
                    "plan": next_plan,
                    "operation": operation,
                    "execution": execution,
                    "verification": verification,
                    "history": history,
                    "message": "The operation succeeded, but Hashtag could not determine a safe next step or confirm overall goal completion.",
                }

            working_plan = dict(next_plan)
            attempt += 1
            working_plan["attempt"] = attempt
            working_plan["mode"] = "goal_continuation"

    @staticmethod
    def _pipeline_version(plan):
        # Preserve the public V1.7-C response version for legacy/deterministic
        # one-operation callers while semantic continuation uses the G9-S8
        # pipeline version. The implementation remains one pipeline.
        if isinstance(plan, dict) and not bool(plan.get("provider_used")):
            return "1.7-C"
        return BodyRecoveryPipeline.VERSION

    @classmethod
    def _completion_evidence(cls, request, *, history, context=None):
        """Prove a provider completion claim from observable execution evidence."""
        text = str(request or "").strip().lower()
        items = list(history or [])
        if not items and isinstance(context, dict):
            items = list(context.get("history") or [])
            if not items:
                observations = context.get("observations") or []
                for obs in observations:
                    if isinstance(obs, dict):
                        items.append({
                            "operation": obs.get("operation") or {},
                            "execution": {"status": obs.get("status", "")},
                            "verification": obs.get("verification") or {},
                        })

        operations = []
        for item in items:
            if not isinstance(item, dict):
                continue
            op = item.get("operation") or {}
            if not isinstance(op, dict):
                continue
            name = str(op.get("operation") or op.get("capability") or "").strip()
            execution = item.get("execution") or {}
            verification = item.get("verification") or {}
            status = str(execution.get("status", "") or "").strip().lower()
            ok = status == "success" and bool(verification.get("ok"))
            result = execution.get("result")
            if isinstance(result, dict) and result.get("returncode") is not None:
                try:
                    ok = ok and int(result.get("returncode")) == 0
                except (TypeError, ValueError):
                    pass
            operations.append({"name": name, "ok": ok})

        mutation_caps = {
            "repository.write_file", "filesystem.write", "filesystem.create",
            "filesystem.delete", "filesystem.move", "filesystem.copy",
            "repository.create_branch", "repository.commit",
            "github.file.write", "github.file.delete", "github.commit.create",
            "github.branch.create", "github.pull_request.create",
            "github.deploy_core", "repository.deploy_core",
            # Existing V10/V11 text and format transformations are also
            # successful mutations even though they are not repository/file
            # capabilities. Keep this derived from operation semantics until
            # capability metadata exposes a formal mutation category.
            "text.replace", "text.regex_replace", "text.remove_digits",
            "text.remove_letters", "format.remove_duplicates",
            "format.remove_number_only", "format.keep_before",
            "format.keep_after", "format.lowercase", "format.uppercase",
            "format.join_blocks", "format.sort_lines", "format.pick_fields",
        }
        test_caps = {"repository.run_tests", "tests.run", "github.run_tests"}
        read_caps = {
            "repository.identify", "repository.inspect", "repository.list_files",
            "repository.read_file", "repository.search", "filesystem.inspect",
            "filesystem.list", "filesystem.read", "github.file.read",
            "github.files.list", "github.repository.inspect", "github.search",
            "github.commits.list", "github.branches.list",
        }

        # Reuse the existing generic goal-intent vocabulary; this is not a
        # G9-S8 phrase rule. Remove filesystem/path tokens before intent
        # detection so names such as "Hashtag-Test" do not turn a read request
        # into an execution/test requirement. The provider still chooses the
        # actual operations.
        intent_text = text
        import re
        intent_text = re.sub(r"[A-Za-z]:\\[^\s]+", " ", intent_text)
        intent_text = re.sub(r"https?://[^\s]+", " ", intent_text)

        def has_intent(terms):
            for term in terms:
                term = str(term).strip().lower()
                if not term:
                    continue
                pattern = r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?![A-Za-z0-9_])"
                if re.search(pattern, intent_text):
                    return True
            return False

        wants_change = has_intent(GoalCapabilityPlanner.INTENTS["write"])
        wants_run = has_intent(GoalCapabilityPlanner.INTENTS["execute"])
        wants_read = has_intent(GoalCapabilityPlanner.INTENTS["read"])
        wants_list = has_intent(GoalCapabilityPlanner.INTENTS["list"])

        mutation = [i for i, x in enumerate(operations) if x["ok"] and x["name"] in mutation_caps]
        tests_ok = [i for i, x in enumerate(operations) if x["ok"] and x["name"] in test_caps]
        tests_failed = [i for i, x in enumerate(operations) if x["name"] in test_caps and not x["ok"]]
        reads = [i for i, x in enumerate(operations) if x["ok"] and x["name"] in read_caps]
        lists = [i for i, x in enumerate(operations) if x["ok"] and x["name"] in {"repository.list_files", "filesystem.list", "github.files.list"}]

        missing = []
        if wants_change and not mutation:
            missing.append("successful modification")
        if wants_run and not tests_ok:
            missing.append("successful test/execution")
        if wants_read and not reads:
            missing.append("successful read/inspection")
        if wants_list and not lists:
            missing.append("successful listing")

        if tests_failed:
            last_failed = max(tests_failed)
            if not mutation or not any(m > last_failed for m in mutation):
                missing.append("modification after the observed test failure")
            if not any(t > last_failed and mutation and any(m > last_failed and m < t for m in mutation) for t in tests_ok):
                missing.append("successful test after the modification")

        return {
            "ok": not missing,
            "missing": missing,
            "operations": [x["name"] for x in operations],
            "wants_change": wants_change,
            "wants_run": wants_run,
            "wants_read": wants_read,
            "wants_list": wants_list,
        }

    def _execute_plan(
        self,
        plan: Dict[str, Any],
        *,
        body_id: Optional[str],
        task_id: Optional[str],
        approval_scope: str,
    ) -> Dict[str, Any]:
        operations = plan.get("operations") or []

        if not operations:
            raise BodyRecoveryError(
                "Recovery produced no executable operation."
            )

        data = operations[0]

        operation = Operation(
            operation=str(
                data.get("operation", "")
            ),
            arguments=dict(
                data.get("arguments") or {}
            ),
            reason=str(
                data.get("reason", "")
            ),
            source=str(
                data.get("source", "brain")
            ),
            provenance=str(
                data.get("provenance", "v11")
            ),
            preconditions=list(
                data.get("preconditions") or []
            ),
        )

        try:
            return self.body_router.execute(
                operation,
                body_id=body_id,
                task_id=task_id,
                approval_scope=approval_scope,
            )
        except Exception as exc:
            return {
                "status": "error",
                "result": None,
                "error": str(exc),
                "operation": operation.as_dict() if hasattr(operation, "as_dict") else {},
            }

    @staticmethod
    def _verification_execution(
        execution: Dict[str, Any],
        input_text: str,
    ) -> Dict[str, Any]:
        """
        Adapt a Body result to the existing verifier's execution shape.

        Preserve the Body status/error so the verifier can distinguish
        success from permission_required, denied, and error states.
        """

        execution = execution or {}
        result = execution.get("result")

        if isinstance(result, dict):
            output = (
                result.get("text")
                if "text" in result
                else result.get("output")
            )

            if output is None:
                output = result.get("stdout")

            if output is None and result.get("stderr"):
                output = result.get("stderr")

            if output is None:
                output = result.get("content", "")

        elif isinstance(result, str):
            output = result

        else:
            output = execution.get("text", "")

        return {
            "status": str(
                execution.get("status", "") or ""
            ),
            "error": execution.get("error"),
            "message": execution.get("message"),
            "ok": execution.get("status") == "success",
            "inputText": str(input_text or ""),
            "text": str(output or ""),
            "bodyResult": execution,
        }

    @staticmethod
    def _output_text(execution: Dict[str, Any]) -> str:
        verification_execution = BodyRecoveryPipeline._verification_execution(
            execution,
            "",
        )
        return verification_execution["text"]

    @staticmethod
    def _first_operation(
        plan: Dict[str, Any],
    ) -> Dict[str, Any]:
        operations = plan.get("operations") or []

        if operations:
            return dict(operations[0])

        return {}

    @staticmethod
    def _actions_to_operations(
        actions,
    ):
        operations = []

        for action in actions:
            if not isinstance(action, dict):
                continue

            capability = str(
                action.get("capability", "")
            ).strip()

            if not capability:
                continue

            operations.append(
                Operation.from_action(action).as_dict()
            )

        return operations

