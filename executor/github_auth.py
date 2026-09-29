"""GitHub Authentication and Browser Detection for Hashtag Executor.

Handles:
1. Automatic detection of logged-in GitHub accounts via Windows Credential Manager and cached tokens.
2. Direct username/password login via automated browser (Playwright) if not logged in.
3. Safe token validation against GitHub API.
"""

from __future__ import annotations

import ctypes
import json
import logging
import os
from ctypes import wintypes
from pathlib import Path
from typing import Any, Dict, Optional

import requests

logger = logging.getLogger("executor.github_auth")

CREDENTIALS_CACHE_FILE = Path(os.path.expanduser("~/.hashtag/github_credentials.json"))


# ----------------------------------------------------------------------
# Windows Credential Manager Reader
# ----------------------------------------------------------------------

class _CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ("Flags", wintypes.DWORD),
        ("Type", wintypes.DWORD),
        ("TargetName", wintypes.LPWSTR),
        ("Comment", wintypes.LPWSTR),
        ("LastWritten", wintypes.FILETIME),
        ("CredentialBlobSize", wintypes.DWORD),
        ("CredentialBlob", ctypes.POINTER(ctypes.c_byte)),
        ("Persist", wintypes.DWORD),
        ("AttributeCount", wintypes.DWORD),
        ("Attributes", ctypes.c_void_p),
        ("TargetAlias", wintypes.LPWSTR),
        ("UserName", wintypes.LPWSTR),
    ]


def _read_windows_credential(target_name: str) -> Optional[dict[str, str]]:
    """Read a credential directly from Windows Credential Manager."""
    try:
        advapi32 = ctypes.windll.advapi32
        CredReadW = advapi32.CredReadW
        CredReadW.argtypes = [
            wintypes.LPWSTR,
            wintypes.DWORD,
            wintypes.DWORD,
            ctypes.POINTER(ctypes.POINTER(_CREDENTIAL)),
        ]
        CredReadW.restype = wintypes.BOOL
        CredFree = advapi32.CredFree
        CredFree.argtypes = [ctypes.c_void_p]

        pcred = ctypes.POINTER(_CREDENTIAL)()
        if CredReadW(target_name, 1, 0, ctypes.byref(pcred)):
            cred = pcred.contents
            blob = bytes(cred.CredentialBlob[: cred.CredentialBlobSize])
            user = cred.UserName or ""
            CredFree(pcred)
            token = blob.decode("utf-8", errors="ignore")
            return {"username": user, "token": token}
    except Exception as exc:
        logger.debug("Failed to read credential %s: %s", target_name, exc)
    return None


def _find_windows_github_credentials() -> Optional[dict[str, str]]:
    """Scan common Windows Credential Manager targets for GitHub."""
    known_targets = [
        "LegacyGeneric:target=GitHub - https://api.github.com/hashtag-movies",
        "LegacyGeneric:target=git:https://github.com",
        "git:https://github.com",
    ]

    # Try known targets first
    for target in known_targets:
        cred = _read_windows_credential(target)
        if cred and cred.get("token"):
            valid, user = validate_token(cred["token"])
            if valid:
                return {
                    "token": cred["token"],
                    "username": user or cred.get("username", ""),
                    "source": f"windows_credential ({target})",
                }

    # Fallback: scan cmdkey /list output for any github targets
    try:
        import subprocess

        res = subprocess.run(["cmdkey", "/list"], capture_output=True, text=True, timeout=5)
        for line in res.stdout.splitlines():
            line_str = line.strip()
            if line_str.startswith("Target:") and ("github" in line_str.lower() or "git" in line_str.lower()):
                t = line_str.replace("Target:", "").strip()
                cred = _read_windows_credential(t)
                if cred and cred.get("token"):
                    valid, user = validate_token(cred["token"])
                    if valid:
                        return {
                            "token": cred["token"],
                            "username": user or cred.get("username", ""),
                            "source": f"windows_credential ({t})",
                        }
    except Exception as exc:
        logger.debug("Scanning cmdkey failed: %s", exc)

    return None


# ----------------------------------------------------------------------
# Token Validation
# ----------------------------------------------------------------------

def validate_token(token: str) -> tuple[bool, str]:
    """Test a GitHub token against api.github.com/user."""
    if not token or not token.strip():
        return False, ""
    try:
        r = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {token.strip()}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "Hashtag-Executor",
            },
            timeout=10,
        )
        if r.status_code == 200:
            user_data = r.json()
            return True, user_data.get("login", "")
    except Exception as exc:
        logger.debug("Token validation error: %s", exc)
    return False, ""


# ----------------------------------------------------------------------
# Persistent Cache
# ----------------------------------------------------------------------

def save_credentials(token: str, username: str, source: str = "user_login") -> None:
    """Save GitHub credentials locally to ~/.hashtag/github_credentials.json."""
    try:
        CREDENTIALS_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "token": token,
            "username": username,
            "source": source,
        }
        CREDENTIALS_CACHE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved GitHub credentials for user %s to cache", username)
    except Exception as exc:
        logger.warning("Failed to save GitHub credentials to cache: %s", exc)


def load_cached_credentials() -> Optional[dict[str, str]]:
    """Load cached credentials if valid."""
    if not CREDENTIALS_CACHE_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_CACHE_FILE.read_text(encoding="utf-8"))
        token = data.get("token", "")
        if token:
            valid, user = validate_token(token)
            if valid:
                return {
                    "token": token,
                    "username": user or data.get("username", ""),
                    "source": "cached_file",
                }
    except Exception as exc:
        logger.debug("Failed to load cached credentials: %s", exc)
    return None


# ----------------------------------------------------------------------
# Auto-Detection Facade
# ----------------------------------------------------------------------

def detect_github_session() -> Optional[dict[str, str]]:
    """Auto-detect GitHub credentials from all available sources.

    Priority:
    1. GITHUB_TOKEN environment variable.
    2. Cached credentials (~/.hashtag/github_credentials.json).
    3. Windows Credential Manager (GitHub Desktop / Git CLI / browser tokens).
    """
    # 1. Environment variable
    env_token = os.getenv("GITHUB_TOKEN", "").strip()
    if env_token:
        valid, user = validate_token(env_token)
        if valid:
            return {
                "token": env_token,
                "username": user,
                "source": "environment_variable",
            }

    # 2. Local cache
    cached = load_cached_credentials()
    if cached:
        return cached

    # 3. Windows Credential Manager
    win_cred = _find_windows_github_credentials()
    if win_cred:
        # Cache for faster subsequent lookups
        save_credentials(win_cred["token"], win_cred["username"], source=win_cred["source"])
        return win_cred

    return None


# ----------------------------------------------------------------------
# Automated Browser Login via Playwright
# ----------------------------------------------------------------------

def login_with_browser(username: str, password: str, headless: bool = True) -> dict[str, Any]:
    """Automate GitHub login in Chrome/Edge using Playwright.

    If 2FA is encountered, the browser will wait or return a challenge status.
    """
    from playwright.sync_api import sync_playwright

    logger.info("Attempting automated GitHub login for %s", username)

    # Use installed Chrome or Edge
    channel = "chrome"

    try:
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(channel=channel, headless=headless)
            except Exception:
                # Fallback to Edge
                browser = p.chromium.launch(channel="msedge", headless=headless)

            context = browser.new_context()
            page = context.new_page()

            page.goto("https://github.com/login", timeout=30000)

            # Fill in credentials
            page.fill('input[name="login"]', username)
            page.fill('input[name="password"]', password)
            page.click('input[type="submit"]')

            # Wait for navigation
            page.wait_for_load_state("networkidle", timeout=15000)

            url = page.url
            if "two-factor" in url or "sessions/two-factor" in url or "verified-device" in url:
                browser.close()
                return {
                    "success": False,
                    "requires_2fa": True,
                    "message": "Two-factor authentication required. Please enter 2FA code or approve prompt.",
                }

            if "login" in url:
                # Check for error message
                error_el = page.query_selector(".flash-error")
                error_msg = error_el.inner_text().strip() if error_el else "Invalid credentials"
                browser.close()
                return {
                    "success": False,
                    "requires_2fa": False,
                    "message": error_msg,
                }

            # Successfully logged in! Extract session cookies
            cookies = context.cookies(["https://github.com"])
            user_session = ""
            for c in cookies:
                if c.get("name") == "user_session":
                    user_session = c.get("value", "")

            browser.close()

            return {
                "success": True,
                "username": username,
                "user_session": user_session,
                "message": "Successfully logged in to GitHub Web",
            }
    except Exception as exc:
        return {
            "success": False,
            "requires_2fa": False,
            "message": f"Browser login failed: {exc}",
        }
