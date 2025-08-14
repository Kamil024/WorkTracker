import hashlib
import db
import os
import json

LOGIN_STATE_FILE = "login_state.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username.strip() or not password.strip():
        return False, "Username and password cannot be empty."

    if db.get_user(username):
        return False, "Username already exists."

    hashed = hash_password(password)
    success = db.insert_user(username, hashed)
    if success:
        return True, "Registration successful."
    return False, "Registration failed."

def login_user(username, password):
    user = db.get_user(username)
    if user and user[2] == hash_password(password):
        return True, "Login successful."
    return False, "Invalid username or password."

def save_login_state(username):
    with open(LOGIN_STATE_FILE, "w") as f:
        json.dump({"username": username}, f)

def load_login_state():
    if os.path.exists(LOGIN_STATE_FILE):
        with open(LOGIN_STATE_FILE, "r") as f:
            data = json.load(f)
            return data.get("username")
    return None

def logout():
    if os.path.exists(LOGIN_STATE_FILE):
        os.remove(LOGIN_STATE_FILE)
