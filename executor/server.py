"""Local Hashtag Executor Body HTTP interface."""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from pydantic import BaseModel, Field
import requests
import uuid
import json
import os

from .body import HashtagBody
from .permissions import PermissionDecision, PermissionScope
from .protocol import Operation
from .console_ui import CONSOLE_HTML
from .connector import pc_connector, generate_client_script


app = FastAPI(
    title="Hashtag the Executor",
    version="1.3.0",
)

body = HashtagBody()


@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "Hashtag the Executor",
        "version": "1.3.0",
        "status": "online",
        "body_id": "hashtag-executor",
        "pc_connected": pc_connector.is_connected,
        "pc_info": pc_connector.system_info,
    }


@app.websocket("/v1/connector/ws")
async def connector_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        raw = await websocket.receive_text()
        data = json.loads(raw)
        info = data.get("info") or {}
        await pc_connector.connect(websocket, info)
        gh_tok = info.get("github_token")
        if gh_tok:
            try:
                from .github import GitHubClient
                from .github_auth import validate_token, save_credentials
                valid, user = validate_token(gh_tok)
                if valid:
                    body.github = GitHubClient(token=gh_tok)
                    save_credentials(gh_tok, user, source="pc_connector")
                    logger.info("GitHub credentials auto-inherited from PC connector: @%s", user)
            except Exception as e:
                logger.warning("Failed inheriting GitHub token: %s", e)
        await websocket.send_text(json.dumps({"type": "ack", "status": "linked"}))
        while True:
            msg = await websocket.receive_text()
            pc_connector.handle_response(json.loads(msg))
    except (WebSocketDisconnect, Exception) as err:
        logger.info("PC Connector WS disconnected: %s", err)
        pc_connector.disconnect()


@app.get("/v1/connector/status")
def connector_status():
    return {
        "ok": True,
        "connected": pc_connector.is_connected,
        "info": pc_connector.system_info,
    }


@app.get("/connect.py", response_class=PlainTextResponse)
def get_connect_py(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return generate_client_script(base_url)


@app.get("/connect.bat", response_class=PlainTextResponse)
def get_connect_bat(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return f"""@echo off
title Hashtag PC Connector
echo ========================================================
echo   HASHTAG PC CONNECTOR - LINKING LOCAL DRIVE TO CLOUD
echo ========================================================
curl -s {base_url}/connect.py -o hashtag_connector.py
if not exist hashtag_connector.py (
    powershell -Command "Invoke-WebRequest -Uri '{base_url}/connect.py' -OutFile 'hashtag_connector.py'"
)
python hashtag_connector.py
if errorlevel 1 py hashtag_connector.py
pause
"""


@app.get("/connect.ps1", response_class=PlainTextResponse)
def get_connect_ps1(request: Request):
    base_url = str(request.base_url).rstrip("/")
    return f"""# Hashtag 1-Click PC Connector
Write-Host "Linking PC to Hashtag Cloud..." -ForegroundColor Cyan
$script = Invoke-RestMethod -Uri '{base_url}/connect.py'
$script | Out-File -FilePath "$env:TEMP\\hashtag_connector.py" -Encoding utf8
if (Get-Command python -ErrorAction SilentlyContinue) {{
    python "$env:TEMP\\hashtag_connector.py"
}} elseif (Get-Command py -ErrorAction SilentlyContinue) {{
    py "$env:TEMP\\hashtag_connector.py"
}} else {{
    Write-Host "Python not found in PATH. Please ensure Python is installed." -ForegroundColor Red
}}
"""


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
        "pc_connected": pc_connector.is_connected,
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
    token = str(payload.get("token", "")).strip()
    if token:
        from .github import GitHubClient
        from .github_auth import validate_token, save_credentials
        valid, user = validate_token(token)
        if not valid:
            raise HTTPException(status_code=400, detail="Invalid GitHub token. Please ensure it has repo access.")
        body.github = GitHubClient(token=token)
        save_credentials(token, user, source="web_console")
        return {"success": True, "message": f"Successfully connected as @{user}!", "user_session": {"username": user, "token": token}}

    username = str(payload.get("username", "")).strip()
    password = str(payload.get("password", "")).strip()
    if username or password:
        return {
            "success": False,
            "message": "GitHub deprecated password logins. Please use a Personal Access Token (PAT) with repo access.",
        }
    raise HTTPException(status_code=400, detail="token is required")


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


CORE_URL = os.getenv("CORE_URL", "https://hashtag-core.onrender.com").rstrip("/")

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
        try:
            data = r.json()
        except Exception:
            data = {"ok": False, "error": r.text[:300] if r.text else f"HTTP {r.status_code}"}
        if r.status_code >= 400:
            if r.status_code == 422 and _is_permission_pause(data):
                return data
            if isinstance(data, dict) and ("ok" in data or "message" in data or "pipeline" in data):
                return data
            raise RuntimeError(data.get("error") or data.get("detail") or str(data))
        return data

    except Exception as exc:
        raise RuntimeError(f"Hashtag Core unavailable at {CORE_URL}: {exc}") from exc

@app.get("/v1/console/core")
def console_core():
    core_info = {}
    try:
        core_info = _core("/health", timeout=15)
    except Exception as exc:
        core_info = {"ok": False, "status": "offline", "error": str(exc), "version": "10.0.0 (offline)", "brain": "Hashtag"}
    return {
        "ok": bool(core_info.get("ok")),
        "core": core_info,
        "body": body.capabilities(),
        "pending_permissions": len(body.permissions.pending()),
    }

@app.get("/v1/console/state")
def console_state():
    """Return lightweight Console state without exposing internal request payloads."""
    return {
        "ok": True,
        "pending_console_permissions": len(console_pending),
        "pending_executor_permissions": len(body.permissions.pending()),
    }


def get_executor_public_url(request: Request = None) -> str:
    url = os.getenv("EXECUTOR_PUBLIC_URL", "") or os.getenv("RENDER_EXTERNAL_URL", "")
    if not url and request:
        try:
            url = str(request.base_url).rstrip("/")
        except Exception:
            pass
    if not url:
        if os.getenv("RENDER") or os.getenv("RENDER_SERVICE_ID"):
            url = "https://executor-awhg.onrender.com"
        else:
            host = os.getenv("HOST", "127.0.0.1")
            port = os.getenv("PORT", "8780")
            url = f"http://{host}:{port}"
    return url.rstrip("/")


@app.post("/v1/console/register")
def console_register(request: Request = None):
    base_url = get_executor_public_url(request)
    return _core("/v1/body/register", {
        "base_url": base_url,
    }, timeout=20)

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
def console_request(payload: dict, request: Request = None):
    text=str(payload.get("request") or payload.get("task") or "").strip()
    if not text: raise HTTPException(status_code=400,detail="Request text is required")
    context = dict(payload.get("context") or {})
    target = context.get("target_repo") or context.get("repository")
    if target and isinstance(target, str):
        body.set_target_repository(target)
    else:
        context["target_repo"] = getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core")
    try:
        console_register(request)
    except Exception as e:
        logger.warning("Auto-registration before request failed: %s", e)
    q={"request":text,"body_id":payload.get("body_id") or "hashtag-executor","context":context}
    try:
        result = _core("/v1/request", q)
    except Exception as e:
        if "Body not registered" in str(e) or "404" in str(e):
            try:
                console_register(request)
                result = _core("/v1/request", q)
            except Exception as e2:
                raise HTTPException(status_code=500, detail=str(e2))
        else:
            raise HTTPException(status_code=500, detail=str(e))
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
        base_url = get_executor_public_url()
        approval = requests.post(
            f"{base_url}/v1/body/permissions/decide",
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

@app.get("/", response_class=HTMLResponse)
@app.get("/console", response_class=HTMLResponse)
@app.get("/permissions", response_class=HTMLResponse)
def console_ui_view():
    return CONSOLE_HTML

from .knowledge_ui import KNOWLEDGE_DASHBOARD_HTML
import urllib.parse

@app.get("/knowledge", response_class=HTMLResponse)
@app.get("/intelligence", response_class=HTMLResponse)
def knowledge_dashboard_view():
    return KNOWLEDGE_DASHBOARD_HTML

@app.get("/v1/knowledge/status")
def knowledge_status_proxy():
    try:
        return _core("/v1/knowledge/status", timeout=15)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "total_learned": 0, "sources": {}, "domains": {}, "recent_stream": [], "recent_usages": []}

@app.get("/v1/knowledge/search")
def knowledge_search_proxy(request: Request):
    q = request.query_params.get("q", "")
    limit = request.query_params.get("limit", "15")
    try:
        return _core(f"/v1/knowledge/search?q={urllib.parse.quote(q)}&limit={limit}", timeout=15)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "results": []}

@app.post("/v1/knowledge/harvest")
def knowledge_harvest_proxy(payload: dict):
    return _core("/v1/knowledge/harvest", payload, timeout=20)

@app.get("/v1/body/evolution/status")
def body_evolution_status_proxy():
    try:
        return _core("/v1/body/evolution/status", timeout=15)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "bodies": []}

@app.post("/v1/body/evolve")
def body_evolve_proxy(payload: dict):
    return _core("/v1/body/evolve", payload, timeout=20)

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8780"))
    uvicorn.run("executor.server:app", host=host, port=port, reload=False)
