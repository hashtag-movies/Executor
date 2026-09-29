import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from .registry import ToolRegistry
from .brain import HashtagBrain
from .verifier import HashtagVerifier
from .memory import MemoryStore
from .provider import ModelProvider
from .learning import SkillLearner
from .sandbox import Sandbox
from .recovery import RecoveryEngine
from .body_client import BodyClient
from .body_router import BodyRouter, BodyRouterError, NoBodyAvailableError
from .body_recovery import BodyRecoveryPipeline, BodyRecoveryError
from .operation_graph_adapter import BrainOperationGraphAdapter
from .operation_graph_executor import OperationGraphExecutor
from .replanner_G7_step3 import OperationGraphReplanner
from .recovery_learning_G7_step5 import RecoveryLearningEngine
from .checkpoint_store import GraphCheckpointStore, CheckpointNotFoundError
from . import config
from .contracts import Operation


# ============================================================
# HASHTAG CORE
# Central brain + shared learning + recovery + body routing
# ============================================================

registry = ToolRegistry()

memory = MemoryStore(
    os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        "memory.json",
    )
)

learner = SkillLearner(memory)
brain = HashtagBrain(memory, learner)
sandbox = Sandbox()
verifier = HashtagVerifier()

provider = ModelProvider(
    config.MODEL_ENDPOINT,
    config.MODEL_NAME,
    config.MODEL_API_KEY,
)

# The ModelProvider supplies semantic understanding; it never executes work.
# HashtagBrain remains authoritative for capability validation and planning,
# while the existing Body/permission/execution pipeline remains unchanged.
brain = HashtagBrain(memory, learner, provider=provider)

recovery = RecoveryEngine()

# V1.6 / V1.7 Body Router
# Core discovers and routes work to replaceable Bodies.
body_router = BodyRouter()

# V1.7-D unified request pipeline
# Reuses the existing Brain, BodyRouter, Verifier and RecoveryEngine.
body_recovery = BodyRecoveryPipeline(
    brain=brain,
    body_router=body_router,
    verifier=verifier,
    recovery=recovery,
)

# V1.8 Gate 4B graph integration.
# Uses the same Brain and BodyRouter; this is not a second planner/runtime.
graph_adapter = BrainOperationGraphAdapter(brain)
graph_executor = OperationGraphExecutor(body_router)

# V1.8 Gate 5 checkpoint/resume store.
# In-process by design for this gate; successful graph nodes survive a
# permission pause and are not executed again when the checkpoint resumes.
checkpoint_store = GraphCheckpointStore()

# Gate 7 recovery learning.
# Reuses the existing MemoryStore + SkillLearner; this is not a
# second memory or learning system.
recovery_learning = RecoveryLearningEngine(memory, learner)

tokens = {}


def safe_remember(event):
    try:
        memory.remember(event)
    except Exception:
        pass


def learn_successful_recovery(tool, request, execution, context=None):
    """Persist only a completed successful Gate 7 recovery."""
    return recovery_learning.learn(
        tool_id=(tool or {}).get("id"),
        request=str(request or ""),
        execution=execution or {},
        capabilities=(tool or {}).get("capabilities", []),
        context=context or {},
    )


def make_graph_replanner(tool, request, input_text, context=None):
    """Build the Gate 7 Step 4 replanner from existing Core components."""
    base_context = dict(context or {})

    def candidate_generator(replan_request):
        original = dict(replan_request.original_operation or {})

        action = {
            "capability": str(original.get("operation") or ""),
            "arguments": dict(original.get("arguments") or {}),
            "reason": str(original.get("reason") or ""),
            "source": str(original.get("source") or "brain"),
        }

        evaluation = dict(replan_request.evaluation or {})
        errors = list(evaluation.get("anomalies") or [])

        reason = str(
            evaluation.get("reason")
            or "Operation outcome was not satisfied."
        )

        errors.append(reason)

        verification = {
            "ok": False,
            "errors": errors,
            "warnings": list(
                evaluation.get("anomalies") or []
            ),
        }

        observation = dict(
            replan_request.observation or {}
        )

        output = observation.get("output")

        try:
            alternative = recovery.replan(
                {"actions": [action]},
                verification,
                str(input_text or ""),
                str(output or ""),
            )
        except Exception:
            alternative = None

        if alternative:
            return alternative

        # The central Brain remains the fallback planner.
        # Gate 7 only supplies structured failure feedback.
        replanning_context = dict(base_context)
        replanning_context["replan"] = replan_request.as_dict()
        replanning_context["replan_reason"] = reason
        replanning_context["failed_operation"] = original

        try:
            return brain.plan(
                tool,
                str(request or ""),
                replanning_context,
            )
        except Exception:
            return {"actions": []}

    return OperationGraphReplanner(
        candidate_generator,
        max_candidates=3,
    )


def graph_completion_evidence(request, graph):
    """Adapt successful graph nodes into the shared goal-evidence contract."""
    history = []
    for node in getattr(graph, "nodes", []) or []:
        if str(getattr(node, "state", "") or "").lower() != "success":
            continue
        operation = getattr(node, "operation", None)
        operation_dict = (
            operation.as_dict()
            if hasattr(operation, "as_dict")
            else dict(operation or {})
        )
        execution = getattr(node, "result", None)
        if not isinstance(execution, dict):
            execution = {"status": "success", "result": execution}
        verification = execution.get("verification")
        if not isinstance(verification, dict):
            verification = {"ok": True, "source": "operation_graph_success"}
        history.append({
            "operation": operation_dict,
            "execution": execution,
            "verification": verification,
        })
    return BodyRecoveryPipeline._completion_evidence(
        request, history=history, context=None
    )


class Handler(BaseHTTPRequestHandler):

    server_version = "HashtagCore/10.0.0"

    # ========================================================
    # HTTP RESPONSE
    # ========================================================

    def _send(self, status, payload):

        body = json.dumps(
            payload,
            ensure_ascii=False,
        ).encode()

        origin = self.headers.get("Origin") or "*"

        if origin == "null" and config.ALLOW_FILE_ORIGIN:
            allow = origin

        elif (
            "*" in config.ALLOWED_ORIGINS
            or origin in config.ALLOWED_ORIGINS
        ):
            allow = origin

        else:
            allow = "null"

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8",
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            allow,
        )

        self.send_header(
            "Vary",
            "Origin",
        )

        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type,X-Hashtag-Key,X-Hashtag-Tool",
        )

        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS",
        )

        self.send_header(
            "Cache-Control",
            "no-store",
        )

        self.send_header(
            "Content-Length",
            str(len(body)),
        )

        self.end_headers()

        if status != 204:
            self.wfile.write(body)

    # ========================================================
    # JSON REQUEST
    # ========================================================

    def _json(self):

        n = min(
            int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            ),
            500000,
        )

        if not n:
            return {}

        return json.loads(
            self.rfile.read(n).decode()
        )

    # ========================================================
    # AUTHORIZATION
    # ========================================================

    def _authorized(self, admin=False):

        if not admin:
            return True

        return (
            (not config.API_KEY)
            or secrets.compare_digest(
                self.headers.get(
                    "X-Hashtag-Key",
                    "",
                ),
                config.API_KEY,
            )
        )

    # ========================================================
    # OPTIONS
    # ========================================================

    def do_OPTIONS(self):
        self._send(204, {})

    # ========================================================
    # GET
    # ========================================================

    def do_GET(self):

        p = urlparse(self.path).path

        # ----------------------------------------------------
        # HEALTH
        # ----------------------------------------------------

        if p == "/health":

            return self._send(
                200,
                {
                    "ok": True,
                    "service": "Hashtag AI Core",
                    "version": "10.0.0",
                    "brain": "Hashtag",
                    "architecture": (
                        "central-routing-shared-learning-"
                        "recovery-engine"
                    ),
                    "registered_tools": len(
                        registry.list()
                    ),
                    "registered_bodies": len(
                        body_router.list_bodies()
                    ),
                    "model_provider_configured": (
                        provider.available()
                    ),
                },
            )

        # ----------------------------------------------------
        # V1.8 GATE 5 CHECKPOINT INSPECTION
        # ----------------------------------------------------

        if p.startswith("/v1/checkpoints/"):
            checkpoint_id = p.rsplit("/", 1)[-1].strip()
            if not checkpoint_id:
                return self._send(
                    400,
                    {"ok": False, "error": "checkpoint_id is required"},
                )
            try:
                checkpoint = checkpoint_store.get(checkpoint_id)
                graph = checkpoint_store.graph(checkpoint_id)
                return self._send(
                    200,
                    {
                        "ok": True,
                        "pipeline": "1.8-G5",
                        "checkpoint": {
                            "checkpoint_id": checkpoint.get("checkpoint_id"),
                            "created_at": checkpoint.get("created_at"),
                            "updated_at": checkpoint.get("updated_at"),
                            "request": checkpoint.get("request"),
                            "body_id": checkpoint.get("body_id"),
                            "approval_scope": checkpoint.get("approval_scope"),
                            "task_id": checkpoint.get("task_id"),
                            "metadata": checkpoint.get("metadata", {}),
                            "graph": graph.as_dict(),
                        },
                    },
                )
            except CheckpointNotFoundError as e:
                return self._send(404, {"ok": False, "error": str(e)})

        # ----------------------------------------------------
        # TOOLS
        # ----------------------------------------------------

        if p == "/v1/tools":

            return self._send(
                200,
                {
                    "ok": True,
                    "tools": registry.public_list(),
                },
            )

        # ----------------------------------------------------
        # V1.7 BODY DISCOVERY
        # ----------------------------------------------------

        if p == "/v1/bodies":

            bodies = body_router.list_bodies()

            return self._send(
                200,
                {
                    "ok": True,
                    "bodies": [
                        body.to_dict()
                        if hasattr(body, "to_dict")
                        else body
                        for body in bodies
                    ],
                    "capabilities": body_router.capabilities(),
                },
            )

        # ----------------------------------------------------
        # LEARNED SKILLS
        # ----------------------------------------------------

        if p == "/v1/skills":

            if not self._authorized(True):

                return self._send(
                    401,
                    {
                        "ok": False,
                        "error": "Unauthorized",
                    },
                )

            return self._send(
                200,
                {
                    "ok": True,
                    "skills": memory.learned(500),
                },
            )

        # ----------------------------------------------------
        # RECENT MEMORY
        # ----------------------------------------------------

        if p == "/v1/memory/recent":

            if not self._authorized(True):

                return self._send(
                    401,
                    {
                        "ok": False,
                        "error": "Unauthorized",
                    },
                )

            return self._send(
                200,
                {
                    "ok": True,
                    "events": memory.recent(200),
                },
            )

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        return self._send(
            404,
            {
                "ok": False,
                "error": "Not found",
            },
        )

    # ========================================================
    # POST
    # ========================================================

    def do_POST(self):

        try:
            data = self._json()

        except Exception as e:

            return self._send(
                400,
                {
                    "ok": False,
                    "error": str(e),
                },
            )

        p = urlparse(self.path).path

        # ====================================================
        # EXISTING TOOL REGISTRATION
        # ====================================================

        if p == "/v1/register":

            manifest = data.get("manifest") or {}

            try:
                registry.register(manifest)

            except Exception as e:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

            token = secrets.token_urlsafe(24)

            tokens[
                manifest.get("id", "")
            ] = {
                "token": token,
                "time": time.time(),
            }

            safe_remember(
                {
                    "event": "tool_registered",
                    "tool_id": manifest.get("id"),
                    "version": manifest.get("version"),
                }
            )

            return self._send(
                200,
                {
                    "ok": True,
                    "tool_id": manifest.get("id"),
                    "token": token,
                    "brain": "Hashtag Core V10.0.0",
                    "tool_count": len(
                        registry.list()
                    ),
                },
            )

        # ====================================================
        # EXISTING HEARTBEAT
        # ====================================================

        if p == "/v1/heartbeat":

            return self._send(
                200,
                {
                    "ok": registry.heartbeat(
                        data.get(
                            "tool_id",
                            "",
                        )
                    )
                },
            )

        # ====================================================
        # V1.7 BODY REGISTRATION
        # ====================================================

        if p == "/v1/body/register":

            base_url = str(
                data.get("base_url") or ""
            ).strip()

            if not base_url:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": "base_url is required",
                    },
                )

            try:

                timeout = float(
                    data.get(
                        "timeout",
                        15,
                    )
                )

                client = BodyClient(
                    base_url,
                    timeout=timeout,
                )

                body = body_router.register(
                    client,
                    refresh=True,
                )

                safe_remember(
                    {
                        "event": "body_registered",
                        "body_id": body.body_id,
                        "version": body.version,
                        "capabilities": body.capabilities,
                    }
                )

                return self._send(
                    200,
                    {
                        "ok": True,
                        "body": body.to_dict(),
                    },
                )

            except Exception as e:

                return self._send(
                    502,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

        # ====================================================
        # V1.7 BODY ROUTING
        # ====================================================

        if p == "/v1/body/route":

            operation = data.get("operation")

            if not operation:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": "operation is required",
                    },
                )

            try:

                core_operation = Operation(
                    operation=str(operation),
                    arguments=dict(data.get("arguments") or {}),
                    reason=str(data.get("reason") or ""),
                    source=str(data.get("source") or "core"),
                    provenance=str(data.get("provenance") or "v11"),
                    preconditions=list(data.get("preconditions") or []),
                )
                selected = body_router.route(
                    core_operation
                )

                if hasattr(
                    selected,
                    "to_dict",
                ):
                    selected = selected.to_dict()

                return self._send(
                    200,
                    {
                        "ok": True,
                        "body": selected,
                    },
                )

            except NoBodyAvailableError as e:

                return self._send(
                    404,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

            except BodyRouterError as e:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

            except Exception as e:

                return self._send(
                    502,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

        # ====================================================
        # V1.7 BODY EXECUTION
        # ====================================================

        if p == "/v1/body/execute":

            operation = data.get("operation")

            if not operation:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": "operation is required",
                    },
                )

            body_id = data.get(
                "body_id"
            )

            request_id = data.get(
                "request_id"
            )

            task_id = data.get(
                "task_id"
            )

            approval_scope = str(
                data.get(
                    "approval_scope",
                    "none",
                )
            )

            try:

                core_operation = Operation(
                    operation=str(operation),
                    arguments=dict(data.get("arguments") or {}),
                    reason=str(data.get("reason") or ""),
                    source=str(data.get("source") or "core"),
                    provenance=str(data.get("provenance") or "v11"),
                    preconditions=list(data.get("preconditions") or []),
                )
                
                result = body_router.execute(
                    core_operation,
                    body_id=body_id,
                    request_id=request_id,
                    task_id=task_id,
                    approval_scope=approval_scope,
                )

                safe_remember(
                    {
                        "event": "body_execution",
                        "body_id": (
                            result.get(
                                "audit",
                                {},
                            ).get(
                                "body_id"
                            )
                            if isinstance(
                                result,
                                dict,
                            )
                            else body_id
                        ),
                        "operation": (
                            result.get(
                                "audit",
                                {},
                            ).get(
                                "operation"
                            )
                            if isinstance(
                                result,
                                dict,
                            )
                            else None
                        ),
                        "status": (
                            result.get(
                                "status"
                            )
                            if isinstance(
                                result,
                                dict,
                            )
                            else None
                        ),
                    }
                )

                response_payload = dict(result) if isinstance(result, dict) else {"result": result}
                response_payload["ok"] = True
                response_payload["body_result"] = result

                return self._send(
                    200,
                    response_payload,
                )

            except NoBodyAvailableError as e:

                return self._send(
                    404,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

            except BodyRouterError as e:

                return self._send(
                    400,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

            except Exception as e:

                return self._send(
                    502,
                    {
                        "ok": False,
                        "error": str(e),
                    },
                )

        # ====================================================
        # V1.8 GATE 5 CHECKPOINT RESUME
        # ====================================================

        if p == "/v1/request/resume":
            checkpoint_id = str(data.get("checkpoint_id") or "").strip()
            if not checkpoint_id:
                return self._send(
                    400,
                    {"ok": False, "error": "checkpoint_id is required"},
                )

            try:
                checkpoint = checkpoint_store.get(checkpoint_id)
                graph = checkpoint_store.graph(checkpoint_id)

                graph_result = graph_executor.execute(
                    graph,
                    body_id=checkpoint.get("body_id"),
                    approval_scope=str(
                        checkpoint.get("approval_scope") or "none"
                    ),
                    task_id=checkpoint.get("task_id"),
                )

                paused = bool(
                    graph_result.get("permission_required")
                    or graph_result.get("paused")
                )
                graph_ok = bool(graph_result.get("ok"))
                goal_evidence = None
                if graph_ok and not paused:
                    goal_evidence = graph_completion_evidence(
                        checkpoint.get("request") or "", graph
                    )
                    graph_ok = bool(goal_evidence.get("ok"))

                if paused:
                    checkpoint_public = checkpoint_store.update(
                        checkpoint_id,
                        graph=graph,
                        metadata={
                            "last_status": "waiting_permission",
                            "resumed": True,
                        },
                    )
                else:
                    checkpoint_public = {
                        "checkpoint_id": checkpoint_id,
                        "graph_id": graph.graph_id,
                        "states": graph.states(),
                        "metadata": {
                            "last_status": (
                                "success" if graph_ok else "failed"
                            ),
                            "resumed": True,
                        },
                    }
                    checkpoint_store.delete(checkpoint_id)

                safe_remember(
                    {
                        "event": "body_request_resume",
                        "request": str(checkpoint.get("request") or "")[:500],
                        "body_id": checkpoint.get("body_id"),
                        "checkpoint_id": checkpoint_id,
                        "ok": graph_ok,
                        "paused": paused,
                        "graph_pipeline": "1.8-G5",
                    }
                )

                return self._send(
                    202 if paused else (200 if graph_ok else 422),
                    {
                        "ok": graph_ok,
                        "paused": paused,
                        "permission_required": bool(
                            graph_result.get("permission_required")
                        ),
                        "resumed": True,
                        "checkpoint_id": (
                            checkpoint_id if paused else None
                        ),
                        "checkpoint": checkpoint_public,
                        "request": checkpoint.get("request"),
                        "tool": checkpoint.get("tool", {}),
                        "body_id": checkpoint.get("body_id"),
                        "pipeline": {
                            "version": "1.8-G5",
                            "verified": graph_ok,
                            "recovered": False,
                            "resumed": True,
                        },
                        "execution": graph_result,
                        "verification": {
                            "ok": graph_ok,
                            "errors": (
                                []
                                if graph_ok
                                else graph_result.get("failed", [])
                            ),
                            "warnings": [],
                            "replan": False,
                        },
                        "history": graph_result.get("history", []),
                        "completion_evidence": goal_evidence,
                        "graph": graph_result.get("graph", graph.as_dict()),
                        "graph_pipeline": "1.8-G5",
                        "message": (
                            "Checkpoint resumed and graph completed successfully."
                            if graph_ok
                            else (
                                "Checkpoint resumed and is still waiting for permission."
                                if paused
                                else "Checkpoint resumed but graph did not complete successfully."
                            )
                        ),
                    },
                )

            except CheckpointNotFoundError as e:
                return self._send(404, {"ok": False, "error": str(e)})
            except NoBodyAvailableError as e:
                return self._send(404, {"ok": False, "error": str(e)})
            except BodyRouterError as e:
                return self._send(400, {"ok": False, "error": str(e)})
            except Exception as e:
                return self._send(502, {"ok": False, "error": str(e)})

        # ====================================================
        # V1.8 / V1.7 UNIFIED REQUEST PIPELINE
        # ====================================================

        if p == "/v1/request":
            # Convenience alias: POST /v1/request with checkpoint_id resumes
            # the exact saved graph rather than planning a new request.
            checkpoint_id = str(data.get("checkpoint_id") or "").strip()
            if checkpoint_id:
                try:
                    checkpoint = checkpoint_store.get(checkpoint_id)
                    graph = checkpoint_store.graph(checkpoint_id)
                    graph_result = graph_executor.execute(
                        graph,
                        body_id=checkpoint.get("body_id"),
                        approval_scope=str(
                            checkpoint.get("approval_scope") or "none"
                        ),
                        task_id=checkpoint.get("task_id"),
                        replanner=make_graph_replanner(
                            checkpoint.get("tool") or {},
                            checkpoint.get("request") or "",
                            checkpoint.get("input_text") or "",
                            checkpoint.get("context") or {},
                        ),
                        max_replans=(
                            checkpoint.get("metadata") or {}
                        ).get("max_replans", 2),
                    )
                    paused = bool(
                        graph_result.get("permission_required")
                        or graph_result.get("paused")
                    )
                    graph_ok = bool(graph_result.get("ok"))
                    goal_evidence = None
                    if graph_ok and not paused:
                        goal_evidence = graph_completion_evidence(
                            checkpoint.get("request") or "", graph
                        )
                        graph_ok = bool(goal_evidence.get("ok"))
                    if paused:
                        checkpoint_public = checkpoint_store.update(
                            checkpoint_id,
                            graph=graph,
                            metadata={
                                "last_status": "waiting_permission",
                                "resumed": True,
                            },
                        )
                    else:
                        checkpoint_public = {
                            "checkpoint_id": checkpoint_id,
                            "graph_id": graph.graph_id,
                            "states": graph.states(),
                            "metadata": {
                                "last_status": (
                                    "success" if graph_ok else "failed"
                                ),
                                "resumed": True,
                            },
                        }
                        checkpoint_store.delete(checkpoint_id)

                    return self._send(
                        202 if paused else (200 if graph_ok else 422),
                        {
                            "ok": graph_ok,
                            "paused": paused,
                            "permission_required": bool(
                                graph_result.get("permission_required")
                            ),
                            "resumed": True,
                            "checkpoint_id": (
                                checkpoint_id if paused else None
                            ),
                            "checkpoint": checkpoint_public,
                            "request": checkpoint.get("request"),
                            "tool": checkpoint.get("tool", {}),
                            "body_id": checkpoint.get("body_id"),
                            "pipeline": {
                                "version": "1.8-G5",
                                "verified": graph_ok,
                                "recovered": False,
                                "resumed": True,
                            },
                            "execution": graph_result,
                            "history": graph_result.get("history", []),
                            "graph": graph_result.get("graph", graph.as_dict()),
                            "graph_pipeline": "1.8-G5",
                        },
                    )
                except CheckpointNotFoundError as e:
                    return self._send(404, {"ok": False, "error": str(e)})
                except Exception as e:
                    return self._send(502, {"ok": False, "error": str(e)})
            request = str(
                data.get("request")
                or data.get("task")
                or ""
            ).strip()

            if not request:
                return self._send(
                    400,
                    {"ok": False, "error": "request is required"},
                )

            context = data.get("context") or {}
            body_id = data.get("body_id")
            tool_id = data.get("tool_id")

            # V1.7-E: a registered Body is a first-class execution target.
            tool = None

            if body_id:
                try:
                    body_info = body_router.get_body(body_id)
                except Exception:
                    body_info = None

                if body_info is None:
                    return self._send(
                        404,
                        {
                            "ok": False,
                            "error": f"Body not registered: {body_id}",
                        },
                    )

                capabilities = list(
                    getattr(body_info, "capabilities", []) or []
                )
                tool = {
                    "id": body_info.body_id,
                    "name": body_info.name,
                    "version": body_info.version,
                    "description": "Hashtag Body execution target",
                    "capabilities": [
                        {"id": str(cap)}
                        if isinstance(cap, str)
                        else dict(cap)
                        for cap in capabilities
                    ],
                }

            elif tool_id:
                tool = registry.get(tool_id)

            if not tool:
                ranked = registry.rank(request)
                tool = ranked[0] if ranked else None

            # If no legacy Tool was found, let the central Brain inspect
            # registered Bodies using their advertised capabilities.
            if not tool:
                for candidate in body_router.list_bodies():
                    capabilities = list(
                        getattr(candidate, "capabilities", []) or []
                    )
                    candidate_tool = {
                        "id": candidate.body_id,
                        "name": candidate.name,
                        "version": candidate.version,
                        "description": "Hashtag Body execution target",
                        "capabilities": [
                            {"id": str(cap)}
                            if isinstance(cap, str)
                            else dict(cap)
                            for cap in capabilities
                        ],
                    }
                    try:
                        preview = brain.plan(
                            candidate_tool,
                            request,
                            context,
                        )
                    except Exception:
                        preview = {}

                    if preview.get("actions"):
                        tool = candidate_tool
                        body_id = candidate.body_id
                        break

            if not tool:
                return self._send(
                    404,
                    {
                        "ok": False,
                        "error": "No compatible tool or body registered",
                    },
                )

            if not body_id and tool.get("id"):
                registered_body = body_router.get_body(tool.get("id"))
                if registered_body is not None:
                    body_id = registered_body.body_id

            approval_scope = str(
                data.get("approval_scope", "none")
            )
            task_id = data.get("task_id")
            input_text = str(
                data.get("inputText")
                or context.get("inputText")
                or ""
            )

            try:
                # Gate 4B first asks the existing Brain for its normal plan
                # and adapts that exact plan into the V1.8 graph contract.
                planned = graph_adapter.plan(
                    tool=tool,
                    request=request,
                    input_text=input_text,
                    context=context,
                )

                actions = planned.get("actions") or []
                operation_count = len(
                    planned.get("operations") or []
                )

                # Preserve the complete V1.7 BodyRecovery path for the
                # existing single-operation case. This keeps verification,
                # bounded recovery, and the existing response contract
                # unchanged while Gate 4B introduces multi-operation graphs.
                if operation_count <= 1:
                    result = body_recovery.execute(
                        tool=tool,
                        request=request,
                        context=context,
                        body_id=body_id,
                        approval_scope=approval_scope,
                        task_id=task_id,
                        input_text=input_text,
                        max_replans=data.get("max_replans"),
                    )

                    pipeline_info = result.get("pipeline", {})
                    paused = bool(
                        result.get("permission_required")
                        or result.get("paused")
                        or pipeline_info.get("permission_required")
                        or pipeline_info.get("paused")
                    )

                    safe_remember(
                        {
                            "event": "body_request",
                            "request": request[:500],
                            "tool_id": tool.get("id"),
                            "body_id": body_id,
                            "ok": result.get("ok"),
                            "attempt": pipeline_info.get("attempt"),
                            "verified": pipeline_info.get("verified"),
                            "recovered": pipeline_info.get("recovered"),
                            "paused": paused,
                            "graph_pipeline": "1.8-G4B",
                            "operation_count": operation_count,
                        }
                    )

                    return self._send(
                        202 if paused else (200 if result.get("ok") else 422),
                        {
                            "ok": result.get("ok", False),
                            "paused": paused,
                            "permission_required": paused,
                            "request": request,
                            "tool": {
                                "id": tool.get("id"),
                                "name": tool.get("name"),
                                "version": tool.get("version"),
                            },
                            "body_id": body_id,
                            "pipeline": pipeline_info,
                            "plan": result.get("plan", {}),
                            "operation": result.get("operation", {}),
                            "execution": result.get("execution", {}),
                            "verification": result.get("verification", {}),
                            "history": result.get("history", []),
                            "observations": result.get("observations", []),
                            "completed_operations": result.get("completed_operations", []),
                            "context": result.get("context") or context,
                            "graph": planned.get("operationGraph", {}),
                            "graph_pipeline": "1.8-G4B",
                            "operation_count": operation_count,
                            "message": result.get("message"),
                        },
                    )

                # Multi-operation plans use the existing graph executor.
                # Gate 5 checkpoints the exact graph when Body permission
                # pauses execution, so completed nodes are never repeated.
                graph = graph_adapter.graph_from_plan(planned)

                graph_result = graph_executor.execute(
                    graph,
                    body_id=body_id,
                    approval_scope=approval_scope,
                    task_id=task_id,
                    replanner=make_graph_replanner(
                        tool,
                        request,
                        input_text,
                        context,
                    ),
                    max_replans=data.get("max_replans"),
                )

                graph_ok = bool(graph_result.get("ok"))
                paused = bool(
                    graph_result.get("permission_required")
                    or graph_result.get("paused")
                )

                learning_result = learn_successful_recovery(
                    tool,
                    request,
                    graph_result,
                    context,
                )

                goal_evidence = None
                if graph_ok and not paused:
                    goal_evidence = graph_completion_evidence(request, graph)
                    graph_ok = bool(goal_evidence.get("ok"))

                checkpoint_public = None
                checkpoint_id = None

                if paused:
                    checkpoint_public = checkpoint_store.create(
                        graph=graph,
                        request=request,
                        tool={
                            "id": tool.get("id"),
                            "name": tool.get("name"),
                            "version": tool.get("version"),
                        },
                        body_id=body_id,
                        approval_scope=approval_scope,
                        task_id=task_id,
                        input_text=input_text,
                        context=context,
                        metadata={
                            "pipeline": "1.8-G5",
                            "operation_count": operation_count,
                            "last_status": "waiting_permission",
                        },
                    )
                    checkpoint_id = checkpoint_public.get("checkpoint_id")

                graph_status = {
                    "version": "1.8-G5",
                    "verified": graph_ok,
                    "recovered": False,
                    "attempt": 1,
                    "operation_count": operation_count,
                    "paused": paused,
                }

                safe_remember(
                    {
                        "event": "body_request",
                        "request": request[:500],
                        "tool_id": tool.get("id"),
                        "body_id": body_id,
                        "ok": graph_ok,
                        "attempt": 1,
                        "verified": graph_ok,
                        "recovered": False,
                        "paused": paused,
                        "checkpoint_id": checkpoint_id,
                        "graph_pipeline": "1.8-G5",
                        "operation_count": operation_count,
                    }
                )

                return self._send(
                    202 if paused else (200 if graph_ok else 422),
                    {
                        "ok": graph_ok,
                        "paused": paused,
                        "permission_required": bool(
                            graph_result.get("permission_required")
                        ),
                        "checkpoint_id": checkpoint_id,
                        "checkpoint": checkpoint_public,
                        "request": request,
                        "tool": {
                            "id": tool.get("id"),
                            "name": tool.get("name"),
                            "version": tool.get("version"),
                        },
                        "body_id": body_id,
                        "pipeline": graph_status,
                        "plan": planned,
                        "operation": (
                            planned.get("operations", [])[0]
                            if planned.get("operations")
                            else {}
                        ),
                        "execution": graph_result,
                        "verification": {
                            "ok": graph_ok,
                            "errors": (
                                []
                                if graph_ok
                                else graph_result.get("failed", [])
                            ),
                            "warnings": [],
                            "replan": False,
                        },
                        "history": graph_result.get("history", []),
                        "completion_evidence": goal_evidence,
                        "graph": graph_result.get("graph", {}),
                        "graph_pipeline": "1.8-G5",
                        "operation_count": operation_count,
                        "message": (
                            "Multi-operation graph executed successfully."
                            if graph_ok
                            else (
                                "Multi-operation graph paused for permission; checkpoint saved."
                                if paused
                                else "Multi-operation graph execution did not complete successfully."
                            )
                        ),
                    },
                )

            except BodyRecoveryError as e:
                return self._send(422, {"ok": False, "error": str(e)})
            except NoBodyAvailableError as e:
                return self._send(404, {"ok": False, "error": str(e)})
            except BodyRouterError as e:
                return self._send(400, {"ok": False, "error": str(e)})
            except Exception as e:
                return self._send(502, {"ok": False, "error": str(e)})

        # ====================================================
        # EXISTING TOOL ROUTING
        # ====================================================

        if p == "/v1/route":

            task = str(
                data.get("task")
                or data.get("request")
                or ""
            ).strip()

            ranked = registry.rank(task)

            selected = (
                ranked[0]
                if ranked
                else None
            )

            if not selected:

                return self._send(
                    404,
                    {
                        "ok": False,
                        "error": (
                            "No tool bodies registered"
                        ),
                    },
                )

            return self._send(
                200,
                {
                    "ok": True,
                    "tool": {
                        "id": selected.get(
                            "id"
                        ),
                        "name": selected.get(
                            "name"
                        ),
                        "version": selected.get(
                            "version"
                        ),
                    },
                    "candidates": [
                        {
                            "id": t.get("id"),
                            "name": t.get("name"),
                            "version": t.get(
                                "version"
                            ),
                        }
                        for t in ranked[:5]
                    ],
                },
            )

        # ====================================================
        # EXISTING PLAN
        # ====================================================

        if p == "/v1/plan":

            req = str(
                data.get(
                    "request",
                    "",
                )
            ).strip()

            tool = (
                registry.get(
                    data.get("tool_id")
                )
                if data.get("tool_id")
                else None
            )

            route = None

            if not tool:

                ranked = registry.rank(req)

                tool = (
                    ranked[0]
                    if ranked
                    else None
                )

                if tool:

                    route = {
                        "selected_tool": tool.get(
                            "id"
                        ),
                        "candidates": [
                            t.get("id")
                            for t in ranked[:5]
                        ],
                    }

            if not tool:

                return self._send(
                    404,
                    {
                        "ok": False,
                        "error": (
                            "No compatible tool body registered"
                        ),
                    },
                )

            result = brain.plan(
                tool,
                req,
                data.get("context") or {},
            )

            result["attempt"] = 1

            if route:
                result["route"] = route

            sample = str(
                (
                    data.get("context") or {}
                ).get(
                    "inputText"
                )
                or ""
            )

            if sample and result.get(
                "actions"
            ):

                try:

                    sim = sandbox.apply(
                        sample,
                        result["actions"],
                    )

                    result["simulation"] = {
                        "ok": True,
                        "outputPreview": sim[:500],
                        "changed": sim != sample,
                    }

                except Exception as e:

                    result["simulation"] = {
                        "ok": False,
                        "error": str(e),
                    }

            safe_remember(
                {
                    "event": "plan",
                    "tool_id": tool["id"],
                    "request": req[:500],
                    "attempt": 1,
                    "action_count": len(
                        result.get(
                            "actions",
                            [],
                        )
                    ),
                }
            )

            return self._send(
                200,
                result,
            )

        # ====================================================
        # EXISTING VERIFY
        # ====================================================

        if p == "/v1/verify":

            plan = (
                data.get("plan")
                or {}
            )

            execution = (
                data.get("execution")
                or {}
            )

            v = verifier.verify(
                plan,
                execution,
            )

            if v.get("ok"):

                tool_id = (
                    data.get("tool_id")
                    or plan.get("tool")
                    or ""
                )

                tool = (
                    registry.get(tool_id)
                    or {}
                )

                learned = (
                    learner.learn_from_success(
                        tool_id,
                        data.get(
                            "request"
                        )
                        or plan.get(
                            "request"
                        )
                        or "",
                        plan,
                        v,
                        capabilities=tool.get(
                            "capabilities",
                            [],
                        ),
                    )
                )

                if learned:

                    v["learned"] = {
                        "stored": True,
                        "scope": "shared",
                        "signature": learned[
                            "intent"
                        ],
                        "required_capabilities": (
                            learned[
                                "required_capabilities"
                            ]
                        ),
                    }

            safe_remember(
                {
                    "event": "verification",
                    "ok": v.get("ok"),
                    "errors": v.get(
                        "errors",
                        [],
                    )[:3],
                }
            )

            return self._send(
                200,
                v,
            )

        # ====================================================
        # EXISTING RECOVERY / REPLAN
        # ====================================================

        if p == "/v1/replan":

            plan = (
                data.get("plan")
                or {}
            )

            verification = (
                data.get("verification")
                or {}
            )

            inp = str(
                data.get(
                    "inputText"
                )
                or ""
            )

            out = str(
                data.get(
                    "outputText"
                )
                or ""
            )

            alt = recovery.replan(
                plan,
                verification,
                inp,
                out,
            )

            if not alt:

                return self._send(
                    200,
                    {
                        "ok": False,
                        "replan": False,
                        "message": (
                            "Hashtag could not find "
                            "a safe alternative plan."
                        ),
                        "attempt": (
                            int(
                                data.get(
                                    "attempt",
                                    1,
                                )
                            )
                            + 1
                        ),
                    },
                )

            new = dict(plan)

            new["actions"] = alt[
                "actions"
            ]

            new["attempt"] = (
                int(
                    data.get(
                        "attempt",
                        1,
                    )
                )
                + 1
            )

            new["mode"] = "recovery"

            new["recoveryReason"] = (
                alt["reason"]
            )

            safe_remember(
                {
                    "event": "replan",
                    "attempt": new[
                        "attempt"
                    ],
                    "reason": alt[
                        "reason"
                    ],
                }
            )

            return self._send(
                200,
                {
                    "ok": True,
                    "replan": True,
                    "plan": new,
                },
            )

        # ====================================================
        # NOT FOUND
        # ====================================================

        return self._send(
            404,
            {
                "ok": False,
                "error": "Not found",
            },
        )


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    print("==========================================")
    print("         HASHTAG AI CORE V10.0.0")
    print("==========================================")
    print("Running at http://{}:{}".format(
        config.HOST,
        config.PORT,
    ))
    print("Central Hashtag brain is ready.")
    print(
        "One brain -> many bodies -> shared learning -> recovery"
    )
    print(
        "Body Router -> live Body discovery -> execution"
    )

    ThreadingHTTPServer(
        (
            config.HOST,
            config.PORT,
        ),
        Handler,
    ).serve_forever()

