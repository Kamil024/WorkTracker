import sqlite3

DB_NAME = "users.db"

def connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# ---------- Schema Creation ----------
def create_user_table():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        conn.commit()

def create_task_table():
    """Create tasks table with richer fields; keep backward-compat columns."""
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT,
                category TEXT,
                location TEXT,
                notes TEXT,
                notify TEXT,
                status TEXT DEFAULT 'Pending',
                start_date TEXT,
                due_date TEXT,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

def migrate_schema_if_needed():
    """Add any missing columns to support the richer task model and user_id migration."""
    def has_column(cursor, table, col):
        cursor.execute(f"PRAGMA table_info({table})")
        return any(r[1] == col for r in cursor.fetchall())

    with connect() as conn:
        cur = conn.cursor()

        # Ensure tasks has all new columns
        needed_cols = [
            ("description", "TEXT"),
            ("priority", "TEXT"),
            ("category", "TEXT"),
            ("location", "TEXT"),
            ("notes", "TEXT"),
            ("notify", "TEXT"),
            ("status", "TEXT DEFAULT 'Pending'"),
            ("user_id", "INTEGER"),
            ("username", "TEXT"),
        ]
        for col, coltype in needed_cols:
            if not has_column(cur, "tasks", col):
                cur.execute(f"ALTER TABLE tasks ADD COLUMN {col} {coltype}")

        # Ensure foreign keys pragma on
        cur.execute("PRAGMA foreign_keys = ON")

        conn.commit()

# ---------- User Ops ----------
def get_user(username):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, username, password FROM users WHERE username = ?", (username,))
        return cur.fetchone()

def insert_user(username, password_hash):
    try:
        with connect() as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password_hash))
        return True
    except sqlite3.IntegrityError as e:
        print(f"[DB] insert_user integrity error: {e}")
        return False
    except Exception as e:
        print(f"[DB] insert_user error: {e}")
        return False

def get_all_users():
    import sqlite3
    conn = sqlite3.connect("your_database.db")  # Use your actual DB path
    cursor = conn.cursor()
    cursor.execute("SELECT username, password FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [{"username": row[0], "password": row[1]} for row in rows]

# ---------- Task Ops ----------
def add_task(user_id, username, title, start_date, due_date,
            description=None, priority=None, category=None, location=None,
            notes=None, notify=None, status="Pending"):
    # Ensure due_date is not empty
    if not due_date:
        raise ValueError("Due date is required.")
    
    with connect() as conn:
        conn.execute("""
            INSERT INTO tasks (user_id, username, title, description, priority, category, location,
                               notes, notify, status, start_date, due_date, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (user_id, username, title, description, priority, category, location,
              notes, notify, status, start_date, due_date))

def get_tasks(user_id=None, username=None, completed=0):
    """Fetch tasks with extended fields like description, notes, etc."""
    with connect() as conn:
        cur = conn.cursor()
        if user_id is not None:
            cur.execute("""
                SELECT id, title, start_date, due_date, completed, status, priority, category, description, notes, notify
                FROM tasks
                WHERE (user_id = ? OR (user_id IS NULL AND username = ?)) AND completed = ?
                ORDER BY due_date IS NULL, due_date ASC
            """, (user_id, username or "", completed))
        else:
            cur.execute("""
                SELECT id, title, start_date, due_date, completed, status, priority, category, description, notes, notify
                FROM tasks
                WHERE username = ? AND completed = ?
                ORDER BY due_date IS NULL, due_date ASC
            """, (username, completed))
        return cur.fetchall()


def get_completed_tasks(user_id=None, username=None):
    return get_tasks(user_id, username, completed=1)

def delete_task(task_id):
    with connect() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

def update_task_completion(task_id, completed: int):
    with connect() as conn:
        conn.execute("UPDATE tasks SET completed = ?, status = ? WHERE id = ?",
                     (completed, "Completed" if completed else "Pending", task_id))

def change_user_password(username, new_password):
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))
        conn.commit()
        return cursor.rowcount > 0  # True if a row was updated
