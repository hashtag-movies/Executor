from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple, Union
"""Local Hashtag Executor Body HTTP interface."""

import sys
from pathlib import Path

_current_dir = Path(__file__).resolve().parent.parent
_core_candidates = [
    _current_dir,
    _current_dir.parent / "Hashtag-core",
    Path.home() / "Hashtag-core",
    Path("/data/data/com.termux/files/home/Hashtag-core"),
    Path(r"C:\Users\ksdav\OneDrive\Documents\GitHub\Hashtag-core"),
]
for _c in _core_candidates:
    if _c.is_dir() and str(_c) not in sys.path:
        sys.path.insert(0, str(_c))

if __package__ is None or __package__ == "":
    __package__ = "executor"

import logging
try:
    from hashtag.structured_logging import (
        setup_structured_logging,
        get_logger,
        LogContext,
        generate_id,
        extract_correlation_ids,
        request_id_var,
        task_id_var,
        operation_id_var,
        session_id_var,
        user_id_var,
        body_id_var,
        extra_fields_var,
    )
except ImportError:
    import time
    def setup_structured_logging(*args, **kwargs): pass
    def get_logger(name): return logging.getLogger(name)
    class LogContext:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
    def generate_id(prefix=""): return f"{prefix}_{int(time.time()*1000)}"
    def extract_correlation_ids(*args, **kwargs): return {}
    class _DummyVar:
        def get(self, default=None): return default
        def set(self, val): pass
    request_id_var = task_id_var = operation_id_var = session_id_var = user_id_var = body_id_var = extra_fields_var = _DummyVar()

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests
import uuid
import json
import os

# Setup structured logging for Executor
_log_level = os.getenv("HASHTAG_LOG_LEVEL", "INFO")
_log_json = os.getenv("HASHTAG_LOG_JSON", "1").lower() in ("1", "true", "yes")
_log_file = os.getenv("HASHTAG_LOG_FILE")
_log_pretty = os.getenv("HASHTAG_LOG_PRETTY", "0").lower() in ("1", "true", "yes")

setup_structured_logging(
    level=_log_level,
    json_output=_log_json,
    pretty=_log_pretty,
    log_file=_log_file,
    console=True,
)

logger = get_logger("executor.server")

logger.info("Hashtag Executor server starting", extra={
    "event": "executor_start",
    "version": "1.3.0",
    "log_level": _log_level,
    "json_output": _log_json,
    "log_file": _log_file,
})

from .body import HashtagBody
from .permissions import PermissionDecision, PermissionScope
from .protocol import Operation
from .console_ui import CONSOLE_HTML
from .studio_ui import STUDIO_HTML
from .connector import pc_connector, generate_client_script, ConnectionState


app = FastAPI(
    title="Hashtag the Executor",
    version="1.3.0",
)

# CORS middleware for console UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Correlation ID middleware for FastAPI
@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    """Extract correlation IDs from headers and set in context."""
    # Extract correlation IDs from headers
    ids = {}
    for key, var in [
        ("X-Request-ID", request_id_var),
        ("X-Task-ID", task_id_var),
        ("X-Operation-ID", operation_id_var),
        ("X-Session-ID", session_id_var),
        ("X-User-ID", user_id_var),
        ("X-Body-ID", body_id_var),
    ]:
        value = request.headers.get(key)
        if value:
            ids[key.lower().replace("-", "_")] = value
            var.set(value)
    
    # Generate missing IDs
    if not request_id_var.get():
        request_id_var.set(generate_id("req_"))
    if not task_id_var.get():
        task_id_var.set(generate_id("task_"))
    
    # Add request info to extra fields
    curr_extra = {}
    try:
        val = extra_fields_var.get()
        if isinstance(val, dict):
            curr_extra = val.copy()
    except Exception:
        curr_extra = {}
    curr_extra.update({
        "request_path": str(request.url.path),
        "request_method": request.method,
        "client_ip": request.client.host if request.client else "unknown",
    })
    extra_fields_var.set(curr_extra)
    
    try:
        response = await call_next(request)
    finally:
        # Clear context vars (optional - they're contextvars so they reset per request)
        pass
    
    # Add correlation IDs to response headers
    for key, value in {
        "request_id": request_id_var.get(),
        "task_id": task_id_var.get(),
        "operation_id": operation_id_var.get(),
        "session_id": session_id_var.get(),
        "user_id": user_id_var.get(),
        "body_id": body_id_var.get(),
    }.items():
        if value:
            response.headers[f"X-Hashtag-{key.replace('_', '-').title()}"] = value
    
    return response

body = HashtagBody()


@app.get("/health")
def health():
    is_conn = bool(pc_connector.is_connected) if hasattr(pc_connector, "is_connected") else False
    primary = pc_connector.get_primary_connection() if (is_conn and hasattr(pc_connector, "get_primary_connection")) else None
    return {
        "ok": True,
        "service": "Hashtag the Executor",
        "version": "1.3.0",
        "status": "online",
        "body_id": "hashtag-executor",
        "pc_connected": is_conn,
        "pc_info": primary.system_info if (primary and is_conn) else {},
    }


@app.websocket("/v1/connector/ws")
async def connector_ws(websocket: WebSocket):
    await websocket.accept()
    connection_id = None
    try:
        raw = await websocket.receive_text()
        data = json.loads(raw)
        info = data.get("info") or {}
        connection_id = await pc_connector.connect(websocket, info)
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
        await websocket.send_text(json.dumps({"type": "ack", "status": "linked", "connection_id": connection_id}))
        while True:
            msg = await websocket.receive_text()
            pc_connector.handle_response(json.loads(msg))
    except (WebSocketDisconnect, Exception) as err:
        logger.info("PC Connector WS disconnected: %s", err)
        if connection_id:
            await pc_connector.disconnect_async(connection_id)
        else:
            await pc_connector.disconnect_async()


@app.get("/v1/connector/status")
def connector_status():
    try:
        is_conn = bool(pc_connector.is_connected) if hasattr(pc_connector, "is_connected") else False
        primary = pc_connector.get_primary_connection() if (is_conn and hasattr(pc_connector, "get_primary_connection")) else None
        active_conns = [c.to_dict() for c in pc_connector.list_connections() if c.is_healthy] if (is_conn and hasattr(pc_connector, "list_connections")) else []
        cnt = len(active_conns)
        if cnt == 0:
            is_conn = False
            primary = None
        info = primary.system_info if (primary and is_conn) else {}
        hostname = primary.hostname if (primary and is_conn) else (info.get("hostname", ""))
        drives = info.get("drives", []) if (primary and is_conn) else []
        return {
            "ok": True,
            "connected": is_conn,
            "connected_count": cnt,
            "total_count": len(pc_connector.list_connections()) if hasattr(pc_connector, "list_connections") else 0,
            "info": info if is_conn else {},
            "hostname": hostname if is_conn else "",
            "drives": drives if is_conn else [],
            "primary_connection_id": primary.connection_id if primary else None,
            "queued_actions": pc_connector.get_queued_actions_count() if hasattr(pc_connector, "get_queued_actions_count") else 0,
            "connections": active_conns if is_conn else [],
        }
    except Exception as e:
        logger.error("Error in connector_status: %s", e)
        return {
            "ok": True,
            "connected": False,
            "connected_count": 0,
            "total_count": 0,
            "info": {},
            "hostname": "",
            "drives": [],
            "primary_connection_id": None,
            "queued_actions": 0,
            "connections": [],
            "error": str(e)
        }


@app.post("/v1/connector/disconnect")
async def connector_disconnect():
    try:
        if hasattr(pc_connector, "disconnect_async"):
            await pc_connector.disconnect_async()
        elif hasattr(pc_connector, "disconnect"):
            pc_connector.disconnect()
        pc_connector._connections.clear()
        pc_connector._primary_connection_id = None
        return {"ok": True, "connected": False, "message": "Disconnected successfully"}
    except Exception as e:
        logger.error("Disconnect error: %s", e)
        pc_connector._connections.clear()
        pc_connector._primary_connection_id = None
        return {"ok": True, "connected": False, "message": f"Disconnected: {e}"}


@app.get("/v1/connector/drives")
async def connector_drives():
    if not pc_connector.is_connected:
        return {"ok": False, "error": "No PC is currently connected", "drives": []}
    try:
        res = await pc_connector.send_action("drives", {})
        return {"ok": True, **res}
    except Exception as e:
        primary = pc_connector.get_primary_connection()
        info = primary.system_info if primary else {}
        drives = info.get("drives") or ["C:\\"]
        return {"ok": True, "drives": drives, "cwd": info.get("cwd", ".")}

@app.post("/v1/connector/action")
async def connector_action(payload: dict):
    action = payload.get("action")
    params = payload.get("params") or {}
    connection_id = payload.get("connection_id")
    if not pc_connector.is_connected:
        return {"ok": False, "error": "No PC is currently connected. Please run the PowerShell or CMD connector command on your PC."}
    try:
        res = await pc_connector.send_action(action, params, connection_id=connection_id)
        return {"ok": True, "result": res}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/v1/connector/files")
async def connector_files(path: str = "."):
    if not pc_connector.is_connected:
        return {"ok": False, "error": "No PC is currently connected"}
    try:
        res = await pc_connector.send_action("list", {"path": path})
        return {"ok": True, "entries": res.get("entries", []), "path": res.get("path", path)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/v1/connector/file")
async def connector_file(path: str):
    if not pc_connector.is_connected:
        return {"ok": False, "error": "No PC is currently connected"}
    try:
        res = await pc_connector.send_action("read", {"path": path})
        return {"ok": True, "content": res.get("content", ""), "path": path}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.post("/v1/connector/file")
async def connector_write_file(request: Request):
    try:
        payload = await request.json()
    except Exception:
        try:
            raw_body = await request.body()
            payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
        except Exception:
            payload = {}
    if isinstance(payload, str):
        try: payload = json.loads(payload)
        except Exception: pass
    if not isinstance(payload, dict):
        payload = {}
    path = payload.get("path")
    content = payload.get("content", "")
    if not pc_connector.is_connected:
        return {"ok": False, "error": "No PC is currently connected"}
    try:
        res = await pc_connector.send_action("write", {"path": path, "content": content})
        return {"ok": True, "result": res}
    except Exception as e:
        return {"ok": False, "error": str(e)}



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



def _get_request_github_client(request: Request, payload: Optional[dict] = None) -> tuple[Any, Optional[str]]:
    token = request.headers.get("X-GitHub-Token")
    if not token and payload and isinstance(payload, dict):
        token = payload.get("token") or payload.get("github_token")
    if not token:
        auth = request.headers.get("Authorization", "")
        if auth.lower().startswith("bearer "):
            candidate = auth[7:].strip()
            if any(candidate.startswith(p) for p in ("ghp_", "gho_", "github_pat_")):
                token = candidate
    if token and str(token).strip():
        from .github import GitHubClient
        tok_str = str(token).strip()
        client = GitHubClient(token=tok_str)
        client.token = tok_str
        return client, tok_str
    return None, None

@app.get("/v1/github/status")
def github_status(request: Request):
    client, token = _get_request_github_client(request)
    if not client:
        return {"connected": False, "username": "", "target_repo": ""}
    try:
        user = client.get_authenticated_user()
        return {
            "connected": True,
            "username": user.get("login", ""),
            "name": user.get("name", "") or user.get("login", ""),
            "avatar_url": user.get("avatar_url", ""),
            "target_repo": "",
            "source": "per_user_token",
        }
    except Exception as exc:
        return {"connected": False, "error": str(exc)}


@app.get("/v1/github/repositories")
@app.get("/v1/github/project/repos")
def github_repositories(request: Request):
    client, token = _get_request_github_client(request)
    if not client:
        return {"ok": True, "connected": False, "repositories": [], "current": ""}
    try:
        repos = client._get("user/repos?per_page=100&affiliation=owner,collaborator,organization_member")
        items = []
        for r in repos:
            items.append({
                "name": r.get("name"),
                "full_name": r.get("full_name"),
                "owner": (r.get("owner") or {}).get("login"),
                "default_branch": r.get("default_branch", "main"),
                "private": r.get("private", False),
            })
        user = {}
        try:
            user = client.get_authenticated_user()
        except Exception:
            pass
        return {
            "ok": True,
            "connected": bool(items or user),
            "repositories": items,
            "user": user,
            "current": items[0]["full_name"] if items else "",
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


@app.get("/v1/github/project/tree")
def github_project_tree(request: Request, repo: str = "", ref: str = "main"):
    client, _ = _get_request_github_client(request)
    client = client or getattr(body, "github", None)
    if not client or not getattr(client, "token", None):
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    target = repo.strip()
    if not target:
        raise HTTPException(status_code=400, detail="Repository required.")
    owner, repo_name = body._resolve_owner_repo({"repository": target})
    try:
        branch_info = client.get_branch(owner, repo_name, ref)
        tree_sha = branch_info["commit"]["commit"]["tree"]["sha"]
        tree_data = client.get_tree(owner, repo_name, tree_sha=tree_sha, recursive=True)
        items = tree_data.get("tree", [])
        return {
            "ok": True,
            "owner": owner,
            "repo": repo_name,
            "full_name": f"{owner}/{repo_name}",
            "ref": ref,
            "tree": items,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/v1/github/project/file")
def github_project_file(request: Request, path: str, repo: str = "", ref: str = "main"):
    client, _ = _get_request_github_client(request)
    client = client or getattr(body, "github", None)
    if not client or not getattr(client, "token", None):
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    target = repo.strip()
    if not target:
        raise HTTPException(status_code=400, detail="Repository required.")
    owner, repo_name = body._resolve_owner_repo({"repository": target})
    try:
        text = client.get_file_text(owner, repo_name, path=path, ref=ref)
        file_info = client.get_file(owner, repo_name, path=path, ref=ref)
        sha = file_info.get("sha") if isinstance(file_info, dict) else None
        return {
            "ok": True,
            "path": path,
            "text": text,
            "sha": sha,
            "owner": owner,
            "repo": repo_name,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/v1/github/project/file")
def github_project_write_file(request: Request, payload: dict):
    client, _ = _get_request_github_client(request, payload)
    client = client or getattr(body, "github", None)
    if not client or not getattr(client, "token", None):
        raise HTTPException(status_code=401, detail="GitHub account not connected.")
    path = str(payload.get("path", "")).strip()
    if not path:
        raise HTTPException(status_code=400, detail="path is required")
    content = str(payload.get("content", ""))
    message = str(payload.get("message", "")).strip() or f"Update {path} via Hashtag Cloud Studio"
    branch = str(payload.get("branch", "main")).strip() or "main"
    repo = str(payload.get("repo", "")).strip()
    if not repo:
        raise HTTPException(status_code=400, detail="repo is required")
    owner, repo_name = body._resolve_owner_repo({"repository": repo})

    try:
        res = client.write_file(
            owner=owner,
            repo=repo_name,
            path=path,
            content=content,
            message=message,
            branch=branch,
        )
        return {"ok": True, "result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/v1/github/project/file")
def github_project_delete_file(payload: dict):
    path = str(payload.get("path", "")).strip()
    if not path:
        raise HTTPException(status_code=400, detail="path is required")
    message = str(payload.get("message", "")).strip() or f"Delete {path} via Hashtag Cloud Studio"
    branch = str(payload.get("branch", "main")).strip() or "main"
    repo = str(payload.get("repo", "")).strip() or getattr(body, "current_target_repo", "hashtag-movies/Hashtag-core")
    owner, repo_name = body._resolve_owner_repo({"repository": repo})

    try:
        res = body.github.delete_file(
            owner=owner,
            repo=repo_name,
            path=path,
            message=message,
            branch=branch,
        )
        return {"ok": True, "result": res}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/v1/github/project/create-repo")
def github_project_create_repo(payload: dict):
    name = str(payload.get("name", "")).strip()
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    description = str(payload.get("description", "")).strip()
    private = bool(payload.get("private", False))
    auto_init = bool(payload.get("auto_init", True))

    try:
        repo_data = body.github.create_repository(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init,
        )
        full_name = repo_data.get("full_name") or f"{repo_data.get('owner', {}).get('login')}/{name}"
        body.set_target_repository(full_name)
        return {"ok": True, "repo": repo_data, "full_name": full_name}
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


CORE_URL = os.getenv("CORE_URL", "http://127.0.0.1:8775").rstrip("/")

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
    core_url = os.getenv("CORE_URL", "http://127.0.0.1:8775")
    if "127.0.0.1" in core_url or "localhost" in core_url:
        return f"http://127.0.0.1:{os.getenv('PORT', '8780')}"
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
    base_url = f"http://127.0.0.1:{os.getenv('PORT', '8780')}"
    try:
        return _core("/v1/body/register", {"base_url": base_url}, timeout=10)
    except Exception:
        pub_url = get_executor_public_url(request)
        return _core("/v1/body/register", {"base_url": pub_url}, timeout=20)

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
    # AUTO-HEAL: If Core returned JSON indicating body not registered, re-register and retry
    if isinstance(result, dict) and not result.get("ok") and "Body not registered" in str(result.get("error")):
        try:
            console_register(request)
            result = _core("/v1/request", q)
        except Exception:
            pass
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

try:
    from . import auth
except ImportError:
    try:
        import auth
    except ImportError:
        auth = None

@app.get("/v1/auth/me")
def auth_me(request: Request):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.query_params.get("token", "")
    user_data = auth.verify_token(token) if (auth and token) else None
    user = auth.get_user_by_id(user_data["sub"]) if (auth and user_data) else None
    return {"ok": True, "authenticated": user is not None, "user": user}

@app.post("/v1/auth/email/register")
async def auth_register(request: Request):
    data = await request.json()
    email = data.get("email", "")
    password = data.get("password", "")
    name = data.get("name", "")
    res = auth.register_with_email(email, password, name) if auth else {"ok": False, "error": "Auth unavailable"}
    return res

@app.post("/v1/auth/email/login")
async def auth_login(request: Request):
    data = await request.json()
    email = data.get("email", "")
    password = data.get("password", "")
    res = auth.login_with_email(email, password) if auth else {"ok": False, "error": "Auth unavailable"}
    return res

@app.post("/v1/auth/test-activate")
async def auth_test_activate(request: Request):
    data = await request.json()
    tier = data.get("tier", "pro_lifetime")
    user_id = data.get("user_id")
    if not user_id:
        auth_header = request.headers.get("Authorization", "")
        token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.query_params.get("token", "")
        u_data = auth.verify_token(token) if (auth and token) else None
        user_id = u_data.get("sub") if u_data else None

    if not user_id and auth:
        demo_user = auth.register_with_email("demo@hashtagai.online", "demo123456", "Demo Creator")
        if not demo_user.get("ok"):
            demo_user = auth.login_with_email("demo@hashtagai.online", "demo123456")
        user_id = demo_user.get("user", {}).get("id")

    if auth and user_id:
        status = "lifetime" if tier == "pro_lifetime" else "active"
        auth.update_user_tier(user_id, tier, status)
        u = auth.get_user_by_id(user_id)
        new_token = auth.create_token({"sub": user_id, "tier": tier, "email": u["email"]})
        return {"ok": True, "token": new_token, "user": u}
    return {"ok": False, "error": "Could not activate test tier"}

@app.get("/v1/billing/plans")
def billing_plans():
    return {
        "ok": True,
        "plans": [
            {
                "id": "free",
                "name": "Free Starter",
                "price": "$0",
                "period": "forever",
                "description": "Essential cloud IDE for beginner coders and students.",
                "features": ["GitHub Cloud Studio & PC Studio", "Connect 1 Local PC Folder", "Desktop Device Simulator", "5 Cross-Bridge Moves/day", "10 AI Prompts/day"]
            },
            {
                "id": "pro_monthly",
                "name": "Pro Monthly",
                "price": "$5",
                "period": "per month",
                "description": "Full power for everyday developers and creators.",
                "features": ["Everything in Free", "Tablet & Mobile Device Simulators + Rotate", "True Browser Fullscreen", "Unlimited Cross-Bridge Transfers", "Unlimited AI Co-Pilot Assistance", "Unlimited Repositories"]
            },
            {
                "id": "pro_lifetime",
                "name": "Lifetime VIP",
                "price": "$27",
                "period": "one-time payment",
                "badge": "BEST VALUE - LIMITED DEAL",
                "description": "Pay once, keep Pro features forever. Zero recurring fees.",
                "features": ["All Pro Monthly Features FOREVER", "Zero Monthly Fees", "Unlimited Device Simulators & Fullscreen", "Unlimited Transfers & AI Co-Pilot", "VIP Access to Future Features"]
            }
        ]
    }

@app.post("/v1/billing/checkout")
async def billing_checkout(request: Request):
    data = await request.json()
    auth_header = request.headers.get("Authorization", "")
    token = auth_header[7:].strip() if auth_header.startswith("Bearer ") else request.query_params.get("token", "")
    u_data = auth.verify_token(token) if (auth and token) else None
    user_id = u_data.get("sub") if u_data else None
    if not user_id:
        return {"ok": False, "error": "Please sign in first"}
    tier = data.get("tier", "pro_monthly")
    res = auth.get_checkout_url(user_id, tier) if auth else {"ok": False, "error": "Billing service unavailable"}
    return res

@app.post("/v1/billing/webhook")
async def billing_webhook(request: Request):
    data = await request.json()
    raw_body = await request.body()
    sig = request.headers.get("X-Signature", "")
    if auth and auth.LEMONSQUEEZY_WEBHOOK_SECRET:
        if not auth.verify_lemonsqueezy_webhook(raw_body, sig):
            raise HTTPException(status_code=400, detail="Invalid signature")
    res = auth.process_lemonsqueezy_webhook(data) if auth else {"ok": False}
    return res

@app.get("/studio", response_class=HTMLResponse)
@app.get("/github-studio", response_class=HTMLResponse)
def studio_ui_view():
    return HTMLResponse(STUDIO_HTML, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/ai", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
def ai_chat_view():
    try:
        r = requests.get(CORE_URL + "/ai", timeout=15)
        return HTMLResponse(r.text, headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    except Exception:
        return HTMLResponse("<h1>Hashtag AI: Core Master Body unavailable</h1>")

@app.post("/v1/ai/chat")
def ai_chat_proxy(payload: dict):
    return _core("/v1/ai/chat", payload=payload, timeout=45)

@app.get("/v1/ai/status")
def ai_status_proxy():
    return _core("/v1/ai/status", timeout=15)

@app.get("/v1/ai/bodies")
def ai_bodies_proxy():
    return _core("/v1/ai/bodies", timeout=15)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

@app.get("/favicon.ico")
def favicon():
    fav_path = os.path.join(ASSETS_DIR, "hashtag_logo.jpg")
    if os.path.isfile(fav_path):
        with open(fav_path, "rb") as f:
            data = f.read()
        return Response(content=data, media_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})
    return Response(status_code=404)

@app.get("/assets/{filename}")
def serve_asset(filename: str):
    safe_name = os.path.basename(filename)
    asset_path = os.path.join(ASSETS_DIR, safe_name)
    if os.path.isfile(asset_path):
        media_type = "image/jpeg" if safe_name.lower().endswith((".jpg", ".jpeg")) else "image/png"
        with open(asset_path, "rb") as f:
            data = f.read()
        return Response(content=data, media_type=media_type, headers={"Cache-Control": "public, max-age=86400"})
    return Response(status_code=404)

from .knowledge_ui import KNOWLEDGE_DASHBOARD_HTML
import urllib.parse

@app.get("/knowledge", response_class=HTMLResponse)
@app.get("/intelligence", response_class=HTMLResponse)
def knowledge_dashboard_view():
    return HTMLResponse(KNOWLEDGE_DASHBOARD_HTML)

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

@app.get("/v1/autonomous/capabilities")
def autonomous_capabilities_proxy():
    try:
        return _core("/v1/autonomous/capabilities", timeout=15)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "capabilities": []}

@app.post("/v1/autonomous/learn-and-execute")
def autonomous_learn_and_execute_proxy(payload: dict):
    return _core("/v1/autonomous/learn-and-execute", payload, timeout=30)

import threading
import time

def _auto_register_loop():
    time.sleep(3)
    while True:
        try:
            _core("/v1/body/register", {"base_url": f"http://127.0.0.1:{os.getenv('PORT', '8780')}"}, timeout=8)
        except Exception:
            pass
        time.sleep(25)

threading.Thread(target=_auto_register_loop, daemon=True, name="ExecutorAutoRegisterWithCore").start()

@app.get("/v1/system/sync")
@app.post("/v1/system/sync")
def system_sync_endpoint():
    def _async_sync():
        time.sleep(1)
        try:
            import subprocess, sys
            repo_dir = Path(__file__).resolve().parent.parent
            subprocess.run(["git", "fetch", "origin", "main"], cwd=str(repo_dir), timeout=20)
            subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=str(repo_dir), timeout=20)
            time.sleep(1)
            os.execv(sys.executable, [sys.executable, "-m", "executor.server"])
        except Exception as ex:
            logger.error("Sync error: %s", ex)
    threading.Thread(target=_async_sync, daemon=True).start()
    return {"ok": True, "message": "Pulling latest changes and reloading Executor in-place..."}

def _start_autonomous_executor_sync():
    """Continuously checks GitHub for updates every 30s and restarts in-place if new commits exist."""
    def _sync_worker():
        time.sleep(25)
        repo_dir = Path(__file__).resolve().parent.parent
        git_dir = repo_dir / ".git"
        if not git_dir.is_dir():
            return
        import subprocess, sys
        while True:
            try:
                time.sleep(30)
                res = subprocess.run(["git", "fetch", "origin", "main"], cwd=str(repo_dir), capture_output=True, timeout=20)
                if res.returncode == 0:
                    local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(repo_dir), text=True, timeout=10).strip()
                    remote_sha = subprocess.check_output(["git", "rev-parse", "origin/main"], cwd=str(repo_dir), text=True, timeout=10).strip()
                    if local_sha and remote_sha and local_sha != remote_sha:
                        logger.info("Autonomous Executor Sync: Updating to %s and reloading...", remote_sha[:8])
                        subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=str(repo_dir), timeout=20)
                        time.sleep(1)
                        os.execv(sys.executable, [sys.executable, "-m", "executor.server"])
            except Exception as e:
                pass
    threading.Thread(target=_sync_worker, daemon=True, name="AutonomousExecutorSync").start()

_start_autonomous_executor_sync()

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8780"))
    uvicorn.run("executor.server:app", host=host, port=port, reload=False)
