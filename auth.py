import db
import json
import os

LOGIN_STATE_FILE = "login_state.json"

def authenticate_user(username, password):
    """Return user dict if credentials match a user in the database."""
    user = db.authenticate_user(username, password)
    return user

def register_user(username, password):
    """Register a new user if username not taken."""
    return db.register_user(username, password)

def save_login_state(user):
    """Save current logged-in user info to file for auto-login."""
    with open(LOGIN_STATE_FILE, "w") as f:
        json.dump({"username": user["username"]}, f)

def load_login_state():
    """Return username if saved login state exists."""
    if os.path.exists(LOGIN_STATE_FILE):
        try:
            with open(LOGIN_STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("username")
        except Exception:
            return None
    return None

def logout():
    """Clear saved login state."""
    if os.path.exists(LOGIN_STATE_FILE):
        os.remove(LOGIN_STATE_FILE)
