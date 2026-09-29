# Hashtag Core V9 Integration

Tool bodies register their manifest with `POST /v1/register`.

Core endpoints:
- `POST /v1/register`
- `POST /v1/heartbeat`
- `GET /v1/tools`
- `POST /v1/route`
- `POST /v1/plan`
- `POST /v1/verify`
- `POST /v1/replan`
- `GET /v1/skills` (admin)
- `GET /v1/memory/recent` (admin)

Do not embed an administrative API key in a public GitHub Pages body. Public bodies use register/plan/verify; privileged introspection uses `HASHTAG_API_KEY`.
