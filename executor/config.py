"""Configuration for Hashtag the Executor."""
import os
from dataclasses import dataclass
from .github_auth import detect_github_session

@dataclass(frozen=True)
class Settings:
    github_token: str = ""
    github_api_url: str = os.getenv("GITHUB_API_URL", "https://api.github.com")
    github_owner: str = os.getenv("GITHUB_OWNER", "")
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

def get_settings() -> Settings:
    sess = detect_github_session()
    token = sess.get("token", "") if sess else os.getenv("GITHUB_TOKEN", "")
    owner = (sess.get("username", "") if sess else "") or os.getenv("GITHUB_OWNER", "")
    return Settings(
        github_token=token,
        github_owner=owner,
    )
