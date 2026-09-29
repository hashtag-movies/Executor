# Hashtag Core V9 Deployment

## Render
Build: `pip install -r requirements.txt`
Start: `python -m hashtag.server`

Environment:
- `HOST=0.0.0.0`
- Render supplies `PORT`
- `HASHTAG_ALLOWED_ORIGINS=https://hashtag-movies.github.io`
- `HASHTAG_ALLOW_FILE_ORIGIN=false`
- optionally set `HASHTAG_API_KEY` for admin endpoints

Check `/health` and `/v1/tools` on the generated HTTPS URL.
