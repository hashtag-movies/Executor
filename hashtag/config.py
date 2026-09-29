import os
HOST=os.getenv("HOST",os.getenv("HASHTAG_HOST","127.0.0.1"))
PORT=int(os.getenv("PORT",os.getenv("HASHTAG_PORT","8775")))
API_KEY=os.getenv("HASHTAG_API_KEY","")
ALLOW_FILE_ORIGIN=os.getenv("HASHTAG_ALLOW_FILE_ORIGIN","1").lower() in ("1","true","yes","on")
_allowed=os.getenv("HASHTAG_ALLOWED_ORIGINS","*")
ALLOWED_ORIGINS=[x.strip() for x in _allowed.split(",") if x.strip()]
MODEL_ENDPOINT=os.getenv("HASHTAG_MODEL_ENDPOINT","http://127.0.0.1:11434/v1/chat/completions")
MODEL_NAME=os.getenv("HASHTAG_MODEL_NAME","qwen3:4b")
MODEL_API_KEY=os.getenv("HASHTAG_MODEL_API_KEY","")
