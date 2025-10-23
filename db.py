import sqlite3
import json
import os

DB_NAME = "worktracker.db"
SESSION_FILE = "session.json"


def connect():
    return sqlite3.connect(DB_NAME)


def create_user_table():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)


def create_task_table():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                title TEXT,
                start_date TEXT,
                due_date TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)


def migrate_schema_if_needed():
    # Reserved for future schema updates
    create_user_table()
    create_task_table()


# ---------- USER OPERATIONS ----------

def insert_user(username, password):
    try:
        with connect() as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return True
    except Exception as e:
        print(f"[DB] insert_user error: {e}")
        return False


def get_user(username):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()


# ---------- AUTHENTICATION HELPERS ----------

def authenticate_user(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return {"id": user[0], "username": user[1]}
    return None


def register_user(username, password):
    if get_user(username):
        print("[DB] register_user error: username already exists.")
        return False
    return insert_user(username, password)


# ---------- SESSION MANAGEMENT ----------

def save_login_state(user_data):
    """Save the logged-in user's info to a local JSON file."""
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(user_data, f)
    except Exception as e:
        print(f"[DB] save_login_state error: {e}")


def load_login_state():
    """Load the last logged-in user's info."""
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return None


def clear_login_state():
    """Clear saved user session."""
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


# ---------- TASK OPERATIONS ----------

def add_task(user_id, username, title, start_date, due_date):
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO tasks (user_id, username, title, start_date, due_date)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, username, title, start_date, due_date))
        return True
    except Exception as e:
        print(f"[DB] add_task error: {e}")
        return False


def get_tasks(username):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT title, start_date, due_date FROM tasks WHERE username = ?", (username,))
        return cur.fetchall()


# ---------- INIT ----------

def initialize_database():
    migrate_schema_if_needed()
    print("[DB] Database initialized successfully.")
