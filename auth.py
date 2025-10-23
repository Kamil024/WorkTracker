import db
import json
import os

LOGIN_STATE_FILE = "login_state.json"

def authenticate_user(username, password):
    """Return True if credentials match a user in the database."""
    user = db.get_user(username)
    if not user:
        return False
    stored_password = user[2]  # assuming columns: id, username, password
    return stored_password == password

def register_user(username, password):
    """Register a new user if username not taken."""
    if db.get_user(username):
        return False  # already exists
    db.add_user(username, password)
    return True

def save_login_state(username):
    """Save current logged-in user to file for auto-login."""
    with open(LOGIN_STATE_FILE, "w") as f:
        json.dump({"username": username}, f)

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
