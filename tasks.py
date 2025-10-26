"""
Wrapper around db task operations used by the UI.
Keeps backward-compatible function signatures.
"""
import db

def get_tasks_rows(username):
    """
    Returns rows in the UI-friendly format:
    [(title, start_date, due_date, status), ...]
    """
    return db.get_tasks(username) or []

def get_tasks_full_rows(username):
    """
    Return full rows with extended fields:
    [(id, user_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes), ...]
    """
    return db.get_tasks_full(username) or []

def add_new_task(user_id, username, title, start_date, due_date, status="In Progress",
                 description=None, priority="Medium", category=None, estimated_minutes=0):
    """
    Adds a new task. Accepts both the older signature (without extra fields)
    and the new one with description/priority/category/estimated_minutes.
    """
    if not title:
        return False

    # For compatibility: if the caller uses old signature, the extra args will be absent/None.
    return db.add_task(user_id, username, title, start_date, due_date, status,
                       description, priority, category, estimated_minutes)

def delete_task_by_title(username, title):
    return db.delete_task(username, title)
