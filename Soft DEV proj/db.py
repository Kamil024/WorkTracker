import sqlite3

DB_NAME = "users.db"

def connect():
    return sqlite3.connect(DB_NAME)

def create_user_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_task_table():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            title TEXT NOT NULL,
            start_date TEXT,
            due_date TEXT,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def add_task(username, title, start_date, due_date):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tasks (username, title, start_date, due_date, completed)
        VALUES (?, ?, ?, ?, 0)
    """, (username, title, start_date, due_date))
    conn.commit()
    conn.close()

def get_tasks(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, start_date, due_date, completed
        FROM tasks
        WHERE username = ? AND completed = 0
    """, (username,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_completed_tasks(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, start_date, due_date, completed
        FROM tasks
        WHERE username = ? AND completed = 1
    """, (username,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def delete_task(task_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def update_task_completion(task_id, completed):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
    conn.commit()
    conn.close()

def get_user(username):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def insert_user(username, password):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False
