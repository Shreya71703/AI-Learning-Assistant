"""
JWT authentication utilities.

User store: flat JSON file (suitable for demo/portfolio use).
Password hashing: bcrypt (work factor automatically chosen by bcrypt.gensalt).
JWT signing: HS256 with configurable secret from environment.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from utils.config import JWT_SECRET

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

USERS_FILE = os.path.join(os.path.dirname(__file__), "..", "users.json")


# ── User Store ────────────────────────────────────────────────────────────────

def _load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load users file: %s", exc)
        return {}


def _save_users(users: dict) -> None:
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)
    except OSError as exc:
        logger.error("Failed to save users file: %s", exc)
        raise RuntimeError("Could not persist user data") from exc


# ── Password Helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    # bcrypt max input is 72 bytes; truncate to avoid silent truncation issues
    pw_bytes = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pw_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    pw_bytes = plain.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(pw_bytes, hashed.encode("utf-8"))
    except Exception:
        return False


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user(username: str, password: str) -> dict:
    users = _load_users()
    if username.lower() in {k.lower() for k in users}:
        raise ValueError("Username already exists")
    user_id = str(uuid.uuid4())
    users[username] = {
        "id": user_id,
        "username": username,
        "hashed_password": hash_password(password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _save_users(users)
    logger.info("Created user: %s", username)
    return {"id": user_id, "username": username}


def authenticate_user(username: str, password: str) -> dict | None:
    users = _load_users()
    # Case-insensitive username lookup
    matched_key = next((k for k in users if k.lower() == username.lower()), None)
    if not matched_key:
        return None
    user = users[matched_key]
    if not verify_password(password, user["hashed_password"]):
        return None
    return {"id": user["id"], "username": user["username"]}


# ── JWT ───────────────────────────────────────────────────────────────────────

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
    except JWTError:
        return None
