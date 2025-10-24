import sqlite3
import json
import os

DB_NAME = "worktracker.db"
SESSION_FILE = "session.json"

# ---------- DATABASE CONNECTION ----------

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
                status TEXT DEFAULT 'In Progress',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

def migrate_schema_if_needed():
    create_user_table()
    create_task_table()

    # Check if "status" column exists; if not, add it.
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cur.fetchall()]
        if "status" not in columns:
            conn.execute("ALTER TABLE tasks ADD COLUMN status TEXT DEFAULT 'In Progress'")
            print("[DB] Migrated: Added 'status' column to tasks table.")

# ---------- USER OPERATIONS ----------

def insert_user(username, password):
    try:
        with connect() as conn:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
        return True
    except sqlite3.IntegrityError:
        print(f"[DB] Username '{username}' already exists.")
        return False
    except Exception as e:
        print(f"[DB] insert_user error: {e}")
        return False

def get_user(username):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        return cur.fetchone()

def register_user(username, password):
    if get_user(username):
        print("[DB] register_user: username already exists.")
        return False
    return insert_user(username, password)

def authenticate_user(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return {"id": user[0], "username": user[1]}
    return None

# ---------- SESSION MANAGEMENT ----------

def save_login_state(user_data):
    try:
        with open(SESSION_FILE, "w") as f:
            json.dump(user_data, f)
        print("[DB] Login session saved.")
    except Exception as e:
        print(f"[DB] save_login_state error: {e}")

def load_login_state():
    if not os.path.exists(SESSION_FILE):
        return None
    try:
        with open(SESSION_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[DB] load_login_state error: {e}")
        return None

def clear_login_state():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("[DB] Login session cleared.")

# ---------- TASK OPERATIONS ----------

def add_task(user_id, username, title, start_date, due_date, status="In Progress"):
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO tasks (user_id, username, title, start_date, due_date, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, username, title, start_date, due_date, status))
        print(f"[DB] Task added for {username}: {title}")
        return True
    except Exception as e:
        print(f"[DB] add_task error: {e}")
        return False

def get_tasks(username):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT title, start_date, due_date, status FROM tasks WHERE username = ? ORDER BY id DESC",
            (username,)
        )
        return cur.fetchall()

def delete_task(username, title):
    try:
        with connect() as conn:
            conn.execute(
                "DELETE FROM tasks WHERE username = ? AND title = ?",
                (username, title)
            )
        print(f"[DB] Task '{title}' deleted for {username}.")
        return True
    except Exception as e:
        print(f"[DB] delete_task error: {e}")
        return False

# ---------- INIT ----------

def initialize_database():
    migrate_schema_if_needed()
    print("[DB] Database initialized successfully.")
