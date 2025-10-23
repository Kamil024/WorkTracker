import db
import json
import os

LOGIN_STATE_FILE = "login_state.json"

def authenticate_user(username, password):
    """Return username if credentials match, else None."""
    user = db.authenticate_user(username, password)  # returns username or None
    return user

def register_user(username, password):
    """Register a new user if username not taken."""
    return db.register_user(username, password)

def save_login_state(username):
    """Save current logged-in username to file for auto-login."""
    with open(LOGIN_STATE_FILE, "w") as f:
        json.dump({"username": username}, f)

def load_login_state():
    """Return saved username if login state exists."""
    if os.path.exists(LOGIN_STATE_FILE):
        try:
            with open(LOGIN_STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("username")
        except Exception:
            return None
    return None

def logout():
    """Clear saved login state and return True if successful."""
    try:
        if os.path.exists(LOGIN_STATE_FILE):
            os.remove(LOGIN_STATE_FILE)
        return True
    except Exception:
        return False
