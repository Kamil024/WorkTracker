import sqlite3
import json
import os

DB_NAME = "worktracker.db"
SESSION_FILE = "session.json"

# ---------- DATABASE CONNECTION ----------

def connect():
    conn = sqlite3.connect(DB_NAME, timeout=5)
    return conn

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
    # create tasks table with extended fields (idempotent)
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
                description TEXT,
                priority TEXT DEFAULT 'Medium',
                category TEXT,
                estimated_minutes INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

def migrate_schema_if_needed():
    create_user_table()
    create_task_table()

    # Ensure older DBs get the new columns
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA table_info(tasks)")
        columns = [col[1] for col in cur.fetchall()]

        extra_columns = [
            ("status", "TEXT DEFAULT 'In Progress'"),
            ("description", "TEXT"),
            ("priority", "TEXT DEFAULT 'Medium'"),
            ("category", "TEXT"),
            ("estimated_minutes", "INTEGER DEFAULT 0"),
        ]

        for col_name, col_def in extra_columns:
            if col_name not in columns:
                try:
                    conn.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}")
                    print(f"[DB] Migrated: Added '{col_name}' column to tasks table.")
                except Exception as e:
                    print(f"[DB] migrate_schema_if_needed error adding {col_name}: {e}")

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
    # user row: (id, username, password)
    if user and len(user) >= 3 and user[2] == password:
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
            data = json.load(f)
            # Basic validation of structure
            if isinstance(data, dict) and "id" in data and "username" in data:
                return data
    except Exception as e:
        print(f"[DB] load_login_state error: {e}")
    return None

def clear_login_state():
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
            print("[DB] Login session cleared.")
        except Exception as e:
            print(f"[DB] clear_login_state error: {e}")

# ---------- TASK OPERATIONS ----------

def add_task(user_id, username, title, start_date, due_date, status="In Progress",
             description=None, priority="Medium", category=None, estimated_minutes=0):
    """
    Adds a task to the DB. New fields:
      - description (TEXT)
      - priority (TEXT)
      - category (TEXT)
      - estimated_minutes (INTEGER)
    """
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO tasks (user_id, username, title, start_date, due_date, status,
                                   description, priority, category, estimated_minutes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, username, title, start_date, due_date, status,
                  description, priority, category, estimated_minutes))
        print(f"[DB] Task added for {username}: {title}")
        return True
    except Exception as e:
        print(f"[DB] add_task error: {e}")
        return False

def get_tasks(username):
    """
    Return the standard rows used by the UI table:
    (title, start_date, due_date, status)
    """
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT title, start_date, due_date, status FROM tasks WHERE username = ? ORDER BY id DESC",
                (username,)
            )
            return cur.fetchall()
    except Exception as e:
        print(f"[DB] get_tasks error: {e}")
        return []

def get_tasks_full(username):
    """
    Return full task rows including extended fields:
    (id, user_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes)
    """
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, user_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes FROM tasks WHERE username = ? ORDER BY id DESC",
                (username,)
            )
            return cur.fetchall()
    except Exception as e:
        print(f"[DB] get_tasks_full error: {e}")
        return []

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
