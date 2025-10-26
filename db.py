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

def create_rewards_table():
    # rewards table stores exp, level and equipped avatar per user
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS rewards (
                user_id INTEGER PRIMARY KEY,
                exp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                avatar TEXT DEFAULT 'female_1.png',
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

def migrate_schema_if_needed():
    create_user_table()
    create_task_table()
    create_rewards_table()

    # Ensure older DBs get the new columns in tasks table
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

# ---------- REWARDS / EXP OPERATIONS ----------

def ensure_reward_entry(user_id):
    """
    Ensure a rewards row exists for user_id. Returns True if exists/created.
    """
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM rewards WHERE user_id = ?", (user_id,))
            if cur.fetchone() is None:
                cur.execute("INSERT INTO rewards (user_id, exp, level, avatar) VALUES (?, ?, ?, ?)",
                            (user_id, 0, 1, "female_1.png"))
                conn.commit()
                print(f"[DB] Created rewards entry for user_id={user_id}")
        return True
    except Exception as e:
        print(f"[DB] ensure_reward_entry error: {e}")
        return False

def get_reward_data(user_id):
    """
    Returns a dict with keys: user_id, exp, level, avatar
    If no row exists, creates one and returns defaults.
    """
    try:
        ensure_reward_entry(user_id)
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, exp, level, avatar FROM rewards WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if row:
                return {"user_id": row[0], "exp": int(row[1]), "level": int(row[2]), "avatar": row[3]}
    except Exception as e:
        print(f"[DB] get_reward_data error: {e}")
    # fallback defaults
    return {"user_id": user_id, "exp": 0, "level": 1, "avatar": "female_1.png"}

def set_avatar(user_id, avatar_filename):
    """
    Set the equipped avatar for user.
    """
    try:
        ensure_reward_entry(user_id)
        with connect() as conn:
            conn.execute("UPDATE rewards SET avatar = ? WHERE user_id = ?", (avatar_filename, user_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] set_avatar error: {e}")
        return False

def set_level(user_id, level):
    """
    Force set level (and optionally cap it between 1 and 30).
    """
    try:
        level = max(1, min(30, int(level)))
        ensure_reward_entry(user_id)
        with connect() as conn:
            conn.execute("UPDATE rewards SET level = ? WHERE user_id = ?", (level, user_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] set_level error: {e}")
        return False

def add_exp(user_id, amount):
    """
    Adds EXP for the user. Handles level-up logic automatically.
    Returns a dict: {"success": bool, "exp": int, "level": int, "leveled_up": bool}
    Level calculation:
      - level = 1 + (total_exp // 100)
      - capped at level 30
    """
    try:
        amount = int(amount)
    except Exception:
        amount = 0

    try:
        ensure_reward_entry(user_id)
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT exp, level FROM rewards WHERE user_id = ?", (user_id,))
            row = cur.fetchone()
            if not row:
                cur.execute("INSERT INTO rewards (user_id, exp, level, avatar) VALUES (?, ?, ?, ?)",
                            (user_id, amount, 1, "female_1.png"))
                conn.commit()
                total_exp = amount
                old_level = 1
            else:
                total_exp = int(row[0]) + amount
                old_level = int(row[1])

            # compute new level from total_exp
            new_level = 1 + (total_exp // 100)
            if new_level > 30:
                new_level = 30
                # cap EXP to max level range
                total_exp = min(total_exp, 30 * 100 - 1)

            cur.execute("UPDATE rewards SET exp = ?, level = ? WHERE user_id = ?", (total_exp, new_level, user_id))
            conn.commit()

            leveled_up = new_level > old_level
            return {"success": True, "exp": total_exp, "level": new_level, "leveled_up": leveled_up}
    except Exception as e:
        print(f"[DB] add_exp error: {e}")
        return {"success": False, "exp": None, "level": None, "leveled_up": False}

def set_exp(user_id, exp_value):
    """
    Directly set EXP (useful for debugging or admin actions).
    """
    try:
        exp_value = max(0, int(exp_value))
    except Exception:
        exp_value = 0
    try:
        ensure_reward_entry(user_id)
        new_level = 1 + (exp_value // 100)
        if new_level > 30:
            new_level = 30
            exp_value = min(exp_value, 30 * 100 - 1)
        with connect() as conn:
            conn.execute("UPDATE rewards SET exp = ?, level = ? WHERE user_id = ?", (exp_value, new_level, user_id))
            conn.commit()
        return True
    except Exception as e:
        print(f"[DB] set_exp error: {e}")
        return False

# ---------- INIT ----------

def initialize_database():
    migrate_schema_if_needed()
    print("[DB] Database initialized successfully.")
