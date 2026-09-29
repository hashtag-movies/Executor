# Hashtag the Executor — Body V1.2

The first real **Hashtag Body**. Hashtag-core is the brain; this process is the hands.

## Architecture

`Hashtag-core → Body Protocol V1 → Hashtag Executor → PC / GitHub / tools`

The Body contains capabilities, permissions, and execution adapters. It does **not** contain a competing planner, memory, or brain.

## Safety model

Local computer capabilities are **default-deny**. Sensitive operations require an explicit permission decision. Permissions can be scoped to one operation, task, or session. Filesystem access is restricted to roots explicitly supplied by the caller. The local API binds to `127.0.0.1` only.

The V1.2 filesystem capabilities are:

- `filesystem.inspect` — metadata for an authorized path
- `filesystem.list` — list an authorized directory (optionally recursive, bounded)
- `filesystem.search` — search an authorized directory by filename and/or text (bounded)
- `filesystem.read` — read an authorized text file with a byte limit

Terminal execution remains permission-gated. Write/delete/GitHub mutation capabilities remain registered for future approval-gated implementation.

## Run

```powershell
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
python -m pytest -q
python -m uvicorn executor.server:app --host 127.0.0.1 --port 8780
```

Open the local dashboard:

`http://127.0.0.1:8780/permissions`

API documentation:

`http://127.0.0.1:8780/docs`

## API

- `GET /v1/body/status`
- `GET /v1/body/capabilities`
- `GET /v1/body/permissions/pending`
- `POST /v1/body/permissions/decide`
- `POST /v1/body/permissions/revoke`
- `POST /v1/body/execute`
- `GET /permissions`

## Core connection

`executor/core_client.py` provides the HTTP client scaffold for Core registration and result reporting. The next integration milestone is to add authenticated Body registration/heartbeat and Core-to-Body dispatch without moving planning or memory into the Body.

## Roadmap

1. Core ↔ Body Protocol registration/dispatch
2. Interactive permission UI
3. Safe Git/GitHub inspection
4. Isolated workspace + edit engine
5. Test/verification engine
6. GitHub branch/commit/PR operations with approval
7. Research/solution loop owned by Core
8. Generalized learning owned by Core
