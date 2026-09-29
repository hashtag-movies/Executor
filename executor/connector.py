"""Hashtag PC Connector Gateway.

Enables secure, bi-directional communication between the Cloud Executor on Render
and any remote PC without port-forwarding or firewall reconfiguration.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Any, Dict, Optional
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("hashtag.connector")


class PCConnectorManager:
    """Manages active WebSocket bridge connections with remote PCs."""

    def __init__(self):
        self.active_socket: Optional[WebSocket] = None
        self.system_info: Dict[str, Any] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.lock = asyncio.Lock()
        self.loop: Optional[asyncio.AbstractEventLoop] = None

    @property
    def is_connected(self) -> bool:
        return self.active_socket is not None

    async def connect(self, websocket: WebSocket, client_info: Dict[str, Any]):
        self.active_socket = websocket
        self.system_info = client_info or {}
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()
        logger.info("PC Connector linked: %s", self.system_info)

    def disconnect(self):
        self.active_socket = None
        self.system_info = {}
        for req_id, future in self.pending_requests.items():
            if not future.done():
                future.set_exception(ConnectionResetError("PC Connector disconnected"))
        self.pending_requests.clear()
        logger.info("PC Connector unlinked.")

    def send_action_sync(self, action: str, params: Dict[str, Any], timeout: float = 60.0) -> Any:
        """Synchronously execute action on connected PC by bridging into server event loop."""
        if not self.is_connected or not self.loop:
            raise ConnectionError("No PC Connector is currently linked.")
        coro = self.send_action(action, params, timeout=timeout)
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result(timeout=timeout)

    async def send_action(self, action: str, params: Dict[str, Any], timeout: float = 60.0) -> Any:
        """Send an action to the connected PC and await result."""
        if not self.is_connected or self.active_socket is None:
            raise ConnectionError("No PC Connector is currently linked.")

        request_id = uuid.uuid4().hex
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.pending_requests[request_id] = future

        payload = {
            "id": request_id,
            "action": action,
            "params": params,
        }

        try:
            await self.active_socket.send_text(json.dumps(payload))
            return await asyncio.wait_for(future, timeout=timeout)
        finally:
            self.pending_requests.pop(request_id, None)

    def handle_response(self, message_data: Dict[str, Any]):
        request_id = message_data.get("id")
        if not request_id or request_id not in self.pending_requests:
            return

        future = self.pending_requests[request_id]
        if future.done():
            return

        if message_data.get("ok"):
            future.set_result(message_data.get("result"))
        else:
            future.set_exception(RuntimeError(message_data.get("error") or "Remote PC operation failed"))


pc_connector = PCConnectorManager()


def generate_client_script(server_url: str) -> str:
    """Generate self-contained Python connector client script."""
    ws_url = server_url.replace("http://", "ws://").replace("https://", "wss://").rstrip("/") + "/v1/connector/ws"

    return f'''#!/usr/bin/env python3
"""Hashtag PC Connector Client.
Connects your local PC drive and terminal to Hashtag Cloud Executor.
"""
import sys, os, json, platform, time, asyncio

try:
    import websockets
except ImportError:
    print("[Hashtag] Installing websockets dependency...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "websockets>=12.0"])
    import websockets

SERVER_WS = "{ws_url}"

def get_system_info():
    drives = []
    if platform.system() == "Windows":
        import string
        for letter in string.ascii_uppercase:
            drive = f"{{letter}}:\\\\"
            if os.path.exists(drive):
                drives.append(drive)
    else:
        drives = ["/"]
    return {{
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "username": os.getlogin() if hasattr(os, "getlogin") else os.getenv("USERNAME", "user"),
        "drives": drives,
        "cwd": os.getcwd(),
    }}

def handle_action(action, params):
    if action == "inspect":
        path = params.get("path") or "."
        exists = os.path.exists(path)
        is_dir = os.path.isdir(path) if exists else False
        is_file = os.path.isfile(path) if exists else False
        size = os.path.getsize(path) if is_file else 0
        return {{"exists": exists, "is_dir": is_dir, "is_file": is_file, "size": size, "path": path}}

    elif action == "list":
        path = params.get("path") or "."
        if not os.path.exists(path):
            raise FileNotFoundError(f"Directory not found: {{path}}")
        entries = []
        for name in os.listdir(path):
            full = os.path.join(path, name)
            entries.append({{"name": name, "is_dir": os.path.isdir(full), "size": os.path.getsize(full) if os.path.isfile(full) else 0}})
        return {{"entries": entries, "path": path}}

    elif action == "read":
        path = params.get("path")
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {{path}}")
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return {{"content": f.read(), "path": path}}

    elif action == "write":
        path = params.get("path")
        content = params.get("content", "")
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return {{"path": path, "size": len(content), "ok": True}}

    elif action == "collect_path_files":
        source_path = os.path.abspath(params.get("path") or ".")
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Path not found: {{source_path}}")
        if os.path.isfile(source_path):
            with open(source_path, "r", encoding="utf-8", errors="replace") as f:
                return {{os.path.basename(source_path): f.read()}}
        skip = {{"__pycache__", ".pytest_cache", ".git", ".github", ".idea", ".vscode", "node_modules", "dist", "build"}}
        collected = {{}}
        for root, dirs, files in os.walk(source_path):
            dirs[:] = [d for d in dirs if d not in skip and not d.startswith("venv") and not d.startswith("backup")]
            for f in files:
                f_l = f.lower()
                if f_l.endswith((".pyc", ".pyo", ".pyd", ".log", ".tmp")) or ".backup" in f_l or "-backup" in f_l:
                    continue
                fp = os.path.join(root, f)
                try:
                    if os.path.getsize(fp) > 5 * 1024 * 1024: continue
                    rel = os.path.relpath(fp, source_path).replace("\\\\", "/")
                    with open(fp, "r", encoding="utf-8", errors="replace") as f_obj:
                        collected[rel] = f_obj.read()
                except Exception: pass
        return collected

    elif action == "execute":
        import subprocess
        cmd = params.get("command") or ""
        cwd = params.get("cwd") or os.getcwd()
        res = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=120)
        return {{"stdout": res.stdout, "stderr": res.stderr, "returncode": res.returncode}}

    else:
        raise NotImplementedError(f"Action {{action}} not supported")

async def run_client():
    info = get_system_info()
    print("=" * 60)
    print("  HASHTAG PC CONNECTOR")
    print(f"  Hostname: {{info['hostname']}} | OS: {{info['system']}} {{info['release']}}")
    print(f"  Target Hub: {{SERVER_WS}}")
    print("=" * 60)

    while True:
        try:
            print(f"[{{time.strftime('%X')}}] Connecting to Hashtag Cloud Hub...")
            async with websockets.connect(SERVER_WS, max_size=50*1024*1024) as ws:
                await ws.send(json.dumps({{"type": "handshake", "info": info}}))
                print(f"[{{time.strftime('%X')}}] CONNECTED! PC Drive & Terminal linked to Hashtag Console.")
                async for msg in ws:
                    try:
                        data = json.loads(msg)
                        if data.get("type") == "ack":
                            continue
                        req_id = data.get("id")
                        action = data.get("action")
                        if not action:
                            continue
                        params = data.get("params") or {{}}
                        print(f"[Hashtag] Running action: {{action}} -> {{params.get('path') or params.get('command') or ''}}")
                        res = handle_action(action, params)
                        await ws.send(json.dumps({{"id": req_id, "ok": True, "result": res}}))
                    except Exception as exc:
                        await ws.send(json.dumps({{"id": req_id, "ok": False, "error": str(exc)}}))
        except Exception as e:
            print(f"[Hashtag] Connection lost: {{e}}. Retrying in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        print("\\n[Hashtag] Connector stopped.")
'''
