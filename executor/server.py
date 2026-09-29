"""Local Hashtag Executor Body HTTP interface."""

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import requests
import uuid

from .body import HashtagBody
from .permissions import PermissionDecision, PermissionScope
from .protocol import Operation
from .console_ui import CONSOLE_HTML


app = FastAPI(
    title="Hashtag the Executor",
    version="1.3.0",
)

body = HashtagBody()


class OperationRequest(BaseModel):
    operation: str
    arguments: dict = Field(default_factory=dict)
    request_id: str | None = None
    task_id: str | None = None
    approval_scope: str = "none"
    reason: str = ""


class PermissionDecisionRequest(BaseModel):
    request_id: str
    allowed: bool
    scope: str = "once"
    reason: str = ""


@app.get("/v1/body/status")
def status():
    return {
        "status": "online",
        "body": body.capabilities(),
        "pending_permissions": len(
            body.permissions.pending()
        ),
    }


@app.get("/v1/body/capabilities")
def capabilities():
    return body.capabilities()


@app.get("/v1/github/status")
def github_status():
    try:
        user = body.github.get_authenticated_user()
        return {
            "connected": True,
            "username": user.get("login", ""),
            "target_repo": getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core"),
        }
    except Exception as exc:
        return {"connected": False, "error": str(exc)}


@app.get("/v1/github/repositories")
def github_repositories():
    try:
        repos = body.github._get("user/repos?per_page=100&affiliation=owner,collaborator,organization_member")
        items = []
        for r in repos:
            items.append({
                "name": r.get("name"),
                "full_name": r.get("full_name"),
                "owner": r.get("owner", {}).get("login"),
                "default_branch": r.get("default_branch", "main"),
                "private": r.get("private", False),
            })
        return {
            "ok": True,
            "repositories": items,
            "current": getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core"),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "repositories": []}


@app.get("/v1/github/target_repo")
def get_target_repo():
    return {"target_repo": getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core")}


@app.post("/v1/github/target_repo")
def set_target_repo(payload: dict):
    repo = str(payload.get("target_repo", "")).strip()
    if not repo:
        raise HTTPException(status_code=400, detail="target_repo is required")
    current = body.set_target_repository(repo)
    return {"ok": True, "target_repo": current}


@app.post("/v1/github/login")
def github_login(payload: dict):
    from .github_auth import login_with_browser, save_credentials
    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    headless = bool(payload.get("headless", True))
    if not username or not password:
        raise HTTPException(status_code=400, detail="username and password are required")
    res = login_with_browser(username=username, password=password, headless=headless)
    if res.get("success") and res.get("user_session"):
        # Reload GitHubClient with the session if needed
        pass
    return res


@app.post("/v1/github/backup")
def github_backup(payload: dict):
    owner = payload.get("owner", "hashtag-movies")
    repo = payload.get("repo", "Hashtag-core")
    output_path = payload.get("output_path", "")
    ref = payload.get("ref", "main")
    if not output_path:
        raise HTTPException(status_code=400, detail="output_path is required")
    try:
        path = body.github.download_zip(owner=owner, repo=repo, output_path=output_path, ref=ref)
        return {"ok": True, "backup_path": path}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/v1/body/permissions/pending")
def pending_permissions():
    return {
        "pending": [
            r.__dict__ | {
                "scope": r.scope.value
            }
            for r in body.permissions.pending()
        ]
    }


@app.post("/v1/body/permissions/decide")
def decide_permission(
    req: PermissionDecisionRequest,
):
    try:
        scope = PermissionScope(req.scope)

        request = body.permissions.decide(
            req.request_id,
            PermissionDecision(
                req.allowed,
                scope,
                req.reason,
            ),
        )

        return {
            "status": (
                "approved"
                if req.allowed
                else "denied"
            ),
            "request_id": request.request_id,
            "operation": request.operation,
            "resource": request.resource,
            "scope": scope.value,
        }

    except (KeyError, ValueError) as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )


@app.post("/v1/body/permissions/revoke")
def revoke_permissions():
    body.permissions.revoke_all()

    return {
        "status": "revoked"
    }


@app.post("/v1/body/execute")
def execute(req: OperationRequest):
    try:
        operation = Operation(
            operation=req.operation,
            arguments=dict(req.arguments),
            request_id=(
                req.request_id
                or Operation(
                    operation=req.operation
                ).request_id
            ),
            task_id=req.task_id,
            approval_scope=req.approval_scope,
            reason=req.reason,
            source="core",
        )

        result = body.execute(operation)
        response = result.to_dict()

        if result.status == "permission_required":
            pending = body.permissions.pending()

            latest = None

            if pending:
                effective_op = ""
                if isinstance(result.audit, dict):
                    effective_op = str(result.audit.get("operation") or "")

                for request in reversed(pending):
                    if (
                        request.operation == operation.operation
                        or (effective_op and request.operation == effective_op)
                        or (operation.task_id and request.task_id == operation.task_id)
                    ):
                        latest = request
                        break

                if latest is None:
                    latest = pending[-1]

            if latest is not None:
                response["permission_request"] = {
                    "request_id": latest.request_id,
                    "operation": latest.operation,
                    "resource": latest.resource,
                    "purpose": latest.purpose,
                    "scope": latest.scope.value,
                }

        return response

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


CORE_URL = "http://127.0.0.1:8775"

# Console-side pending requests. Core's legacy single-operation recovery
# path does not create a checkpoint, so the Console keeps the original
# natural-language request and can safely retry it after the Executor
# permission is approved. Multi-operation requests still use Core checkpoints.
console_pending: dict[str, dict] = {}

def _is_permission_pause(result: dict) -> bool:
    """Recognize Core's permission-paused response in any known envelope."""
    if not isinstance(result, dict):
        return False
    if result.get("paused") or result.get("permission_required"):
        return True
    pipeline = result.get("pipeline")
    if isinstance(pipeline, dict) and (pipeline.get("paused") or pipeline.get("permission_required")):
        return True
    execution = result.get("execution")
    if isinstance(execution, dict):
        if execution.get("paused") or execution.get("permission_required"):
            return True
        if execution.get("status") == "permission_required":
            return True
        nested = execution.get("result")
        if isinstance(nested, dict) and (nested.get("paused") or nested.get("permission_required") or nested.get("status") == "permission_required"):
            return True
    return False

def _core(path, payload=None, timeout=None):
    try:
        if timeout is None:
            timeout = 60 if payload is None else 1200
        r = requests.get(CORE_URL + path, timeout=timeout) if payload is None else requests.post(CORE_URL + path, json=payload, timeout=timeout)
        data = r.json()
        if r.status_code >= 400:
            if r.status_code == 422 and _is_permission_pause(data):
                return data
            if isinstance(data, dict) and ("ok" in data or "message" in data or "pipeline" in data):
                return data
            raise RuntimeError(data.get("error") or data.get("detail") or str(data))
        return data

    except requests.RequestException as exc:
        raise RuntimeError(f"Hashtag Core unavailable at {CORE_URL}: {exc}") from exc

@app.get("/v1/console/core")
def console_core():
    return {"ok":True,"core":_core("/health"),"body":body.capabilities(),"pending_permissions":len(body.permissions.pending())}

@app.get("/v1/console/state")
def console_state():
    """Return lightweight Console state without exposing internal request payloads."""
    return {
        "ok": True,
        "pending_console_permissions": len(console_pending),
        "pending_executor_permissions": len(body.permissions.pending()),
    }


@app.post("/v1/console/register")
def console_register():
    m=body.capabilities()
    return _core("/v1/body/register",{"body_id":m.get("body_id","hashtag-executor"),"name":m.get("name","Hashtag the Executor"),"protocol_version":m.get("protocol_version","1.1"),"version":m.get("version","1.3.0"),"capabilities":m.get("capabilities",[]),"base_url":"http://127.0.0.1:8780"}, timeout=10)

def _find_permission_request(result: dict):
    if not isinstance(result, dict):
        return None
    direct = result.get("permission_request")
    if isinstance(direct, dict) and direct.get("request_id"):
        return direct
    for key in ("execution", "result", "plan", "graph"):
        value = result.get(key)
        found = _find_permission_request(value) if isinstance(value, dict) else None
        if found:
            return found
    return None


def _remember_console_pending(result: dict, request_payload: dict):
    permission = _find_permission_request(result)
    if not permission:
        return None
    permission_id = str(permission.get("request_id") or "").strip()
    if not permission_id:
        return None
    resumed_payload = dict(request_payload)
    if isinstance(result.get("context"), dict):
        resumed_payload["context"] = dict(result.get("context"))
    console_pending[permission_id] = {
        "console_request_id": uuid.uuid4().hex,
        "payload": resumed_payload,
        "checkpoint_id": str(result.get("checkpoint_id") or "").strip() or None,
    }
    return permission_id


@app.post("/v1/console/request")
def console_request(payload:dict):
    text=str(payload.get("request") or payload.get("task") or "").strip()
    if not text: raise HTTPException(status_code=400,detail="Request text is required")
    context = dict(payload.get("context") or {})
    target = context.get("target_repo") or context.get("repository")
    if target and isinstance(target, str):
        body.set_target_repository(target)
    else:
        context["target_repo"] = getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core")
    try: console_register()
    except Exception: pass
    q={"request":text,"body_id":payload.get("body_id") or "hashtag-executor","context":context}
    if payload.get("task_id"): q["task_id"]=payload["task_id"]
    result = _core("/v1/request",q)
    pending_id = _remember_console_pending(result, q) if _is_permission_pause(result) else None
    if pending_id:
        result["console_permission_request_id"] = pending_id
    return result


@app.post("/v1/console/resume")
def console_resume(payload:dict):
    checkpoint_id=str(payload.get("checkpoint_id") or "").strip()
    if not checkpoint_id: raise HTTPException(status_code=400,detail="checkpoint_id is required")
    return _core("/v1/request/resume",{"checkpoint_id":checkpoint_id})


@app.post("/v1/console/permission/decide")
def console_permission_decide(payload:dict):
    request_id=str(payload.get("request_id") or "").strip()
    allowed=bool(payload.get("allowed"))
    scope=str(payload.get("scope") or "once")
    reason=str(payload.get("reason") or "")
    if not request_id:
        raise HTTPException(status_code=400,detail="request_id is required")

    try:
        decision = api_decision = {
            "request_id": request_id,
            "allowed": allowed,
            "scope": scope,
            "reason": reason,
        }
        approval = requests.post(
            "http://127.0.0.1:8780/v1/body/permissions/decide",
            json=decision,
            timeout=30,
        )
        approval_data = approval.json()
        if approval.status_code >= 400:
            raise RuntimeError(approval_data.get("detail") or approval_data.get("error") or str(approval_data))

        pending = console_pending.get(request_id)
        if not pending and len(console_pending) == 1:
            single_key = next(iter(console_pending.keys()))
            pending = console_pending.get(single_key)
            request_id = single_key

        if not allowed:
            console_pending.pop(request_id, None)
            return {"ok": False, "approved": False, "approval": approval_data, "message": "Permission denied. Task stopped."}
        if not pending:
            return {"ok": False, "approved": True, "approval": approval_data, "message": "Permission approved. No resumable Console request was found."}

        checkpoint_id = pending.get("checkpoint_id")
        if checkpoint_id:
            result = _core("/v1/request/resume", {"checkpoint_id": checkpoint_id})
        else:
            # Core's single-operation pipeline has no checkpoint. Re-submit the
            # exact original natural-language request after the Executor grant.
            retry_payload = dict(pending["payload"])
            retry_payload["approval_scope"] = scope
            result = _core("/v1/request", retry_payload)

        # Only remove the old pending entry after the retry itself has returned.
        console_pending.pop(request_id, None)

        next_pending = _remember_console_pending(result, retry_payload if not checkpoint_id else pending["payload"]) if _is_permission_pause(result) else None
        if next_pending:
            result["console_permission_request_id"] = next_pending

        return {
            "ok": bool(result.get("ok")),
            "approved": True,
            "approval": approval_data,
            "resumed": True,
            "retried": not bool(checkpoint_id),
            "result": result,
        }
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Executor permission service unavailable: {exc}")
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

@app.get("/permissions", response_class=HTMLResponse)
def permission_ui():
    return CONSOLE_HTML

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("executor.server:app", host="127.0.0.1", port=8780, reload=False)
