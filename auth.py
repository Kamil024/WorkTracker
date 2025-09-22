import hashlib
import base64
import os
import db
import json

LOGIN_STATE_FILE = "login_state.json"
PBKDF2_ITERATIONS = 100_000
SALT_BYTES = 16

def _pbkdf2_hash(password: str, salt: bytes | None = None) -> str:
    """Returns base64(salt + derived_key)."""
    if salt is None:
        salt = os.urandom(SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return base64.b64encode(salt + dk).decode("utf-8")

def _pbkdf2_verify(stored_b64: str, password: str) -> bool:
    try:
        raw = base64.b64decode(stored_b64.encode("utf-8"))
        salt, stored_dk = raw[:SALT_BYTES], raw[SALT_BYTES:]
        new_dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
        return stored_dk == new_dk
    except Exception:
        return False

def register_user(username: str, password: str):
    if not username.strip() or not password.strip():
        return False, "Username and password cannot be empty."
    if db.get_user(username):
        return False, "Username already exists."
    hashed = _pbkdf2_hash(password)
    success = db.insert_user(username, hashed)
    if success:
        return True, "Registration successful."
    return False, "Registration failed."

def login_user(username: str, password: str):
    user = db.get_user(username)
    if not user:
        return False, "Invalid username or password.", None
    # user = (id, username, password_hash)
    if _pbkdf2_verify(user[2], password):
        return True, "Login successful.", user
    return False, "Invalid username or password.", None

def save_login_state(username: str):
    try:
        with open(LOGIN_STATE_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": username}, f)
    except Exception as e:
        print(f"[STATE] Failed saving login state: {e}")

def load_login_state():
    try:
        if os.path.exists(LOGIN_STATE_FILE):
            with open(LOGIN_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("username")
    except Exception as e:
        print(f"[STATE] Failed loading login state: {e}")
    return None

def logout() -> bool:
    try:
        if os.path.exists(LOGIN_STATE_FILE):
            os.remove(LOGIN_STATE_FILE)
        return True
    except Exception as e:
        print(f"[STATE] Logout failed: {e}")
        return False
