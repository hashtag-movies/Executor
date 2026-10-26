# -*- coding: utf-8 -*-
"""
Authentication & Subscription Manager for Hashtag Cloud Studio
Supports:
1. Hybrid Authentication (GitHub OAuth, Google OAuth, Email/Password)
2. LemonSqueezy Subscription & Lifetime Billing with Webhooks
3. Zero-dependency SQLite database & HMAC-SHA256 JWT tokens
4. Feature Gating for Free vs Pro ($5/mo & $27 Lifetime)
"""

import base64
import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import threading
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple

# Configuration Constants
DB_PATH = os.getenv("HASHTAG_AUTH_DB", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "auth.db"))

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "").strip()
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "").strip()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

LEMONSQUEEZY_API_KEY = os.getenv("LEMONSQUEEZY_API_KEY", "").strip()
LEMONSQUEEZY_STORE_ID = os.getenv("LEMONSQUEEZY_STORE_ID", "").strip()
LEMONSQUEEZY_WEBHOOK_SECRET = os.getenv("LEMONSQUEEZY_WEBHOOK_SECRET", "").strip()
LEMONSQUEEZY_MONTHLY_VARIANT_ID = os.getenv("LEMONSQUEEZY_MONTHLY_VARIANT_ID", "").strip()
LEMONSQUEEZY_LIFETIME_VARIANT_ID = os.getenv("LEMONSQUEEZY_LIFETIME_VARIANT_ID", "").strip()

# LemonSqueezy Direct Checkout Links (fallback or direct hosted buy URLs)
LEMONSQUEEZY_MONTHLY_CHECKOUT_URL = os.getenv("LEMONSQUEEZY_MONTHLY_CHECKOUT_URL", "").strip()
LEMONSQUEEZY_LIFETIME_CHECKOUT_URL = os.getenv("LEMONSQUEEZY_LIFETIME_CHECKOUT_URL", "").strip()

# Base URL for OAuth callbacks
APP_BASE_URL = os.getenv("APP_BASE_URL", "https://core.hashtagai.online").rstrip("/")

_jwt_secret_cache: Optional[str] = None
_db_lock = threading.RLock()


def get_jwt_secret() -> str:
    global _jwt_secret_cache
    if _jwt_secret_cache:
        return _jwt_secret_cache
    secret = os.getenv("JWT_SECRET", "").strip()
    if secret:
        _jwt_secret_cache = secret
        return secret

    key_file = os.path.join(os.path.dirname(DB_PATH), "jwt_secret.key")
    os.makedirs(os.path.dirname(key_file), exist_ok=True)
    if os.path.exists(key_file):
        try:
            with open(key_file, "r", encoding="utf-8") as f:
                _jwt_secret_cache = f.read().strip()
                if _jwt_secret_cache:
                    return _jwt_secret_cache
        except Exception:
            pass

    new_secret = secrets.token_hex(32)
    try:
        with open(key_file, "w", encoding="utf-8") as f:
            f.write(new_secret)
    except Exception:
        pass
    _jwt_secret_cache = new_secret
    return new_secret


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(s: str) -> bytes:
    padding = "=" * (4 - (len(s) % 4)) if len(s) % 4 != 0 else ""
    return base64.urlsafe_b64decode(s + padding)


def create_token(payload: Dict[str, Any], expires_days: int = 30) -> str:
    secret = get_jwt_secret()
    p = dict(payload)
    p["exp"] = time.time() + (expires_days * 86400)
    p["iat"] = time.time()
    header = {"alg": "HS256", "typ": "JWT"}

    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(p).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    if not token or not isinstance(token, str):
        return None
    parts = token.split(".")
    if len(parts) != 3:
        return None
    header_b64, payload_b64, sig_b64 = parts
    secret = get_jwt_secret()
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(secret.encode("utf-8"), signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_encode(expected_sig), sig_b64):
        return None
    try:
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if payload.get("exp") and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None


def get_db() -> sqlite3.Connection:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_auth_db():
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                password_hash TEXT,
                password_salt TEXT,
                name TEXT,
                avatar_url TEXT,
                provider TEXT DEFAULT 'email',
                provider_id TEXT,
                tier TEXT DEFAULT 'free',
                status TEXT DEFAULT 'active',
                lemon_customer_id TEXT,
                lemon_subscription_id TEXT,
                ai_requests_today INTEGER DEFAULT 0,
                transfers_today INTEGER DEFAULT 0,
                usage_date TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS billing_events (
                id TEXT PRIMARY KEY,
                event_name TEXT,
                user_id TEXT,
                payload_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()
        conn.close()


init_auth_db()


def _hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    if not salt:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return key.hex(), salt


def _verify_password(password: str, password_hash: str, salt: str) -> bool:
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000)
    return hmac.compare_digest(key.hex(), password_hash)


def register_with_email(email: str, password: str, name: str = "") -> Dict[str, Any]:
    email = email.strip().lower()
    if not email or "@" not in email:
        return {"ok": False, "error": "Invalid email address"}
    if len(password) < 6:
        return {"ok": False, "error": "Password must be at least 6 characters"}

    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cur.fetchone():
            conn.close()
            return {"ok": False, "error": "Account already exists with this email. Please sign in."}

        user_id = "usr_" + secrets.token_hex(8)
        pwd_hash, salt = _hash_password(password)
        display_name = name.strip() or email.split("@")[0].capitalize()
        avatar = f"https://api.dicebear.com/7.x/bottts/svg?seed={user_id}"

        cur.execute(
            """
            INSERT INTO users (id, email, password_hash, password_salt, name, avatar_url, provider, tier, status)
            VALUES (?, ?, ?, ?, ?, ?, 'email', 'free', 'active')
            """,
            (user_id, email, pwd_hash, salt, display_name, avatar),
        )
        conn.commit()
        conn.close()

    user_info = get_user_by_id(user_id)
    token = create_token({"sub": user_id, "tier": "free", "email": email})
    return {"ok": True, "token": token, "user": user_info}


def login_with_email(email: str, password: str) -> Dict[str, Any]:
    email = email.strip().lower()
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash, password_salt, tier, status FROM users WHERE email = ?",
            (email,),
        )
        row = cur.fetchone()
        conn.close()

    if not row:
        return {"ok": False, "error": "No account found with this email"}

    user_id = row["id"]
    stored_hash = row["password_hash"]
    stored_salt = row["password_salt"]

    if not stored_hash or not stored_salt or not _verify_password(password, stored_hash, stored_salt):
        return {"ok": False, "error": "Incorrect password"}

    user_info = get_user_by_id(user_id)
    token = create_token({"sub": user_id, "tier": user_info["tier"], "email": email})
    return {"ok": True, "token": token, "user": user_info}


def upsert_oauth_user(provider: str, provider_id: str, email: str, name: str, avatar: str) -> Dict[str, Any]:
    email = email.strip().lower() if email else f"{provider}_{provider_id}@users.hashtag.local"
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE (provider = ? AND provider_id = ?) OR email = ?", (provider, provider_id, email))
        row = cur.fetchone()

        if row:
            user_id = row["id"]
            cur.execute(
                """
                UPDATE users SET name = COALESCE(NULLIF(name, ''), ?), avatar_url = COALESCE(NULLIF(avatar_url, ''), ?), updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (name, avatar, user_id),
            )
        else:
            user_id = "usr_" + secrets.token_hex(8)
            cur.execute(
                """
                INSERT INTO users (id, email, name, avatar_url, provider, provider_id, tier, status)
                VALUES (?, ?, ?, ?, ?, ?, 'free', 'active')
                """,
                (user_id, email, name, avatar, provider, provider_id),
            )
        conn.commit()
        conn.close()

    user_info = get_user_by_id(user_id)
    token = create_token({"sub": user_id, "tier": user_info["tier"], "email": email})
    return {"ok": True, "token": token, "user": user_info}


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, email, name, avatar_url, provider, tier, status, lemon_customer_id,
                   lemon_subscription_id, ai_requests_today, transfers_today, usage_date, created_at
            FROM users WHERE id = ?
            """,
            (user_id,),
        )
        row = cur.fetchone()
        conn.close()

    if not row:
        return None

    # Reset daily counters if day changed
    today = time.strftime("%Y-%m-%d")
    ai_today = row["ai_requests_today"]
    transfers_today = row["transfers_today"]
    if row["usage_date"] != today:
        with _db_lock:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("UPDATE users SET ai_requests_today = 0, transfers_today = 0, usage_date = ? WHERE id = ?", (today, user_id))
            conn.commit()
            conn.close()
        ai_today = 0
        transfers_today = 0

    return {
        "id": row["id"],
        "email": row["email"],
        "name": row["name"] or "Hashtag Creator",
        "avatar_url": row["avatar_url"] or f"https://api.dicebear.com/7.x/bottts/svg?seed={row['id']}",
        "provider": row["provider"],
        "tier": row["tier"] or "free",
        "status": row["status"] or "active",
        "is_pro": (row["tier"] in ("pro_monthly", "pro_lifetime")),
        "is_lifetime": (row["tier"] == "pro_lifetime"),
        "ai_requests_today": ai_today,
        "transfers_today": transfers_today,
        "created_at": row["created_at"],
    }


def update_user_tier(user_id: str, tier: str, status: str = "active", customer_id: str = "", subscription_id: str = "") -> bool:
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users SET tier = ?, status = ?,
                   lemon_customer_id = COALESCE(NULLIF(?, ''), lemon_customer_id),
                   lemon_subscription_id = COALESCE(NULLIF(?, ''), lemon_subscription_id),
                   updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (tier, status, customer_id, subscription_id, user_id),
        )
        conn.commit()
        conn.close()
    return True


def track_feature_usage(user_id: str, feature: str) -> Dict[str, Any]:
    user = get_user_by_id(user_id)
    if not user:
        return {"allowed": False, "error": "User not found"}

    if user["is_pro"]:
        return {"allowed": True, "tier": user["tier"], "remaining": 999999}

    # Free tier limits
    today = time.strftime("%Y-%m-%d")
    with _db_lock:
        conn = get_db()
        cur = conn.cursor()

        if feature == "ai":
            if user["ai_requests_today"] >= 10:
                conn.close()
                return {
                    "allowed": False,
                    "tier": "free",
                    "error": "You've reached your free limit of 10 AI Co-Pilot prompts today. Upgrade to Pro ($5/mo or $27 lifetime) for unlimited AI assistance!",
                }
            cur.execute("UPDATE users SET ai_requests_today = ai_requests_today + 1, usage_date = ? WHERE id = ?", (today, user_id))
            remaining = 10 - (user["ai_requests_today"] + 1)
        elif feature == "transfer":
            if user["transfers_today"] >= 5:
                conn.close()
                return {
                    "allowed": False,
                    "tier": "free",
                    "error": "You've reached your free limit of 5 file transfers today. Upgrade to Pro ($5/mo or $27 lifetime) for unlimited 1-click transfers!",
                }
            cur.execute("UPDATE users SET transfers_today = transfers_today + 1, usage_date = ? WHERE id = ?", (today, user_id))
            remaining = 5 - (user["transfers_today"] + 1)
        else:
            remaining = 0

        conn.commit()
        conn.close()

    return {"allowed": True, "tier": "free", "remaining": remaining}


# -----------------------------------------------------------------------------
# OAuth Handshakes
# -----------------------------------------------------------------------------
def get_github_auth_url(redirect_uri: str) -> str:
    client_id = GITHUB_CLIENT_ID
    if not client_id:
        # Fallback to dev test auth if client_id not set
        return f"/studio?auth_test=github"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "read:user user:email",
        "state": secrets.token_hex(12),
    }
    return "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)


def handle_github_callback(code: str, redirect_uri: str) -> Dict[str, Any]:
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        return {"ok": False, "error": "GitHub OAuth not configured on server"}

    data = urllib.parse.urlencode({
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://github.com/login/oauth/access_token",
        data=data,
        headers={"Accept": "application/json", "User-Agent": "Hashtag-Studio"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        token_res = json.loads(resp.read().decode("utf-8"))

    access_token = token_res.get("access_token")
    if not access_token:
        return {"ok": False, "error": token_res.get("error_description", "Failed to get access token from GitHub")}

    # Get user profile
    u_req = urllib.request.Request(
        "https://api.github.com/user",
        headers={"Authorization": f"Bearer {access_token}", "User-Agent": "Hashtag-Studio"},
    )
    with urllib.request.urlopen(u_req, timeout=15) as resp:
        profile = json.loads(resp.read().decode("utf-8"))

    # Get user email
    email = profile.get("email")
    if not email:
        try:
            e_req = urllib.request.Request(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}", "User-Agent": "Hashtag-Studio"},
            )
            with urllib.request.urlopen(e_req, timeout=15) as resp:
                emails = json.loads(resp.read().decode("utf-8"))
                for e in emails:
                    if e.get("primary") and e.get("verified"):
                        email = e["email"]
                        break
                if not email and emails:
                    email = emails[0].get("email")
        except Exception:
            pass

    return upsert_oauth_user(
        provider="github",
        provider_id=str(profile.get("id")),
        email=email or f"github_{profile.get('id')}@users.hashtag.local",
        name=profile.get("name") or profile.get("login") or "GitHub Developer",
        avatar=profile.get("avatar_url") or "",
    )


def get_google_auth_url(redirect_uri: str) -> str:
    client_id = GOOGLE_CLIENT_ID
    if not client_id:
        return f"/studio?auth_test=google"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "online",
        "state": secrets.token_hex(12),
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)


def handle_google_callback(code: str, redirect_uri: str) -> Dict[str, Any]:
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        return {"ok": False, "error": "Google OAuth not configured on server"}

    data = urllib.parse.urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Hashtag-Studio"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        token_res = json.loads(resp.read().decode("utf-8"))

    id_token = token_res.get("access_token")
    if not id_token:
        return {"ok": False, "error": "Failed to get access token from Google"}

    u_req = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {id_token}", "User-Agent": "Hashtag-Studio"},
    )
    with urllib.request.urlopen(u_req, timeout=15) as resp:
        profile = json.loads(resp.read().decode("utf-8"))

    return upsert_oauth_user(
        provider="google",
        provider_id=str(profile.get("id")),
        email=profile.get("email") or "",
        name=profile.get("name") or "Google User",
        avatar=profile.get("picture") or "",
    )


# -----------------------------------------------------------------------------
# LemonSqueezy Checkout & Webhook Processor
# -----------------------------------------------------------------------------
def get_checkout_url(user_id: str, tier: str, return_url: str = "") -> Dict[str, Any]:
    user = get_user_by_id(user_id)
    if not user:
        return {"ok": False, "error": "User not found"}

    # Use direct checkout URLs if configured
    if tier == "pro_lifetime" and LEMONSQUEEZY_LIFETIME_CHECKOUT_URL:
        sep = "&" if "?" in LEMONSQUEEZY_LIFETIME_CHECKOUT_URL else "?"
        url = f"{LEMONSQUEEZY_LIFETIME_CHECKOUT_URL}{sep}checkout[custom][user_id]={user_id}&checkout[email]={urllib.parse.quote(user['email'])}"
        return {"ok": True, "url": url}

    if tier == "pro_monthly" and LEMONSQUEEZY_MONTHLY_CHECKOUT_URL:
        sep = "&" if "?" in LEMONSQUEEZY_MONTHLY_CHECKOUT_URL else "?"
        url = f"{LEMONSQUEEZY_MONTHLY_CHECKOUT_URL}{sep}checkout[custom][user_id]={user_id}&checkout[email]={urllib.parse.quote(user['email'])}"
        return {"ok": True, "url": url}

    # API dynamic checkout session
    if LEMONSQUEEZY_API_KEY and LEMONSQUEEZY_STORE_ID:
        variant_id = LEMONSQUEEZY_LIFETIME_VARIANT_ID if tier == "pro_lifetime" else LEMONSQUEEZY_MONTHLY_VARIANT_ID
        if variant_id:
            try:
                payload = {
                    "data": {
                        "type": "checkouts",
                        "attributes": {
                            "checkout_data": {
                                "email": user["email"],
                                "name": user["name"],
                                "custom": {
                                    "user_id": user_id,
                                    "tier": tier,
                                }
                            },
                            "product_options": {
                                "redirect_url": return_url or f"{APP_BASE_URL}/studio?billing=success",
                            }
                        },
                        "relationships": {
                            "store": {
                                "data": {
                                    "type": "stores",
                                    "id": str(LEMONSQUEEZY_STORE_ID)
                                }
                            },
                            "variant": {
                                "data": {
                                    "type": "variants",
                                    "id": str(variant_id)
                                }
                            }
                        }
                    }
                }
                req = urllib.request.Request(
                    "https://api.lemonsqueezy.com/v1/checkouts",
                    data=json.dumps(payload).encode("utf-8"),
                    headers={
                        "Authorization": f"Bearer {LEMONSQUEEZY_API_KEY}",
                        "Content-Type": "application/vnd.api+json",
                        "Accept": "application/vnd.api+json",
                        "User-Agent": "Hashtag-Studio"
                    }
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    res_data = json.loads(resp.read().decode("utf-8"))
                    checkout_url = res_data.get("data", {}).get("attributes", {}).get("url")
                    if checkout_url:
                        return {"ok": True, "url": checkout_url}
            except Exception as e:
                print("LemonSqueezy API checkout creation error:", e)

    # Demo / Test Checkout Mode (Instantly activates tier for testing before keys are added)
    demo_url = f"/studio?activate_test_tier={tier}&user_id={user_id}"
    return {
        "ok": True,
        "url": demo_url,
        "is_test_mode": True,
        "note": "LemonSqueezy keys not configured yet. Test activation link generated."
    }


def verify_lemonsqueezy_webhook(raw_payload: bytes, signature_header: str) -> bool:
    if not LEMONSQUEEZY_WEBHOOK_SECRET:
        return False
    digest = hmac.new(LEMONSQUEEZY_WEBHOOK_SECRET.encode("utf-8"), raw_payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(digest, signature_header)


def process_lemonsqueezy_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    meta = payload.get("meta", {})
    event_name = meta.get("event_name", "")
    custom_data = meta.get("custom_data", {})
    user_id = custom_data.get("user_id")

    data_obj = payload.get("data", {})
    attrs = data_obj.get("attributes", {})

    # If user_id not in custom_data, try customer email
    if not user_id:
        user_email = attrs.get("user_email") or attrs.get("customer_email")
        if user_email:
            with _db_lock:
                conn = get_db()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE email = ?", (user_email.strip().lower(),))
                row = cur.fetchone()
                conn.close()
                if row:
                    user_id = row["id"]

    if not user_id:
        return {"ok": False, "error": "No associated user found for webhook event"}

    customer_id = str(attrs.get("customer_id", ""))
    sub_id = str(data_obj.get("id", ""))

    with _db_lock:
        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO billing_events (id, event_name, user_id, payload_json) VALUES (?, ?, ?, ?)",
            (f"evt_{secrets.token_hex(8)}", event_name, user_id, json.dumps(payload)),
        )
        conn.commit()
        conn.close()

    if event_name in ("order_created", "subscription_created"):
        tier = custom_data.get("tier")
        # Detect lifetime by product name or price if tier not set
        if not tier:
            first_item = attrs.get("first_order_item", {})
            p_name = (first_item.get("product_name") or attrs.get("product_name") or "").lower()
            tier = "pro_lifetime" if "lifetime" in p_name else "pro_monthly"

        status = "lifetime" if tier == "pro_lifetime" else "active"
        update_user_tier(user_id, tier, status, customer_id, sub_id)
        return {"ok": True, "action": f"Upgraded user {user_id} to {tier}"}

    elif event_name in ("subscription_updated", "subscription_resumed"):
        sub_status = attrs.get("status", "active")
        status = "active" if sub_status in ("active", "on_trial") else sub_status
        tier = "pro_monthly" if status == "active" else "free"
        update_user_tier(user_id, tier, status, customer_id, sub_id)
        return {"ok": True, "action": f"Updated user {user_id} subscription to {status}"}

    elif event_name in ("subscription_cancelled", "subscription_expired"):
        update_user_tier(user_id, "free", "cancelled", customer_id, sub_id)
        return {"ok": True, "action": f"Downgraded user {user_id} to free"}

    return {"ok": True, "action": f"Acknowledged event {event_name}"}
