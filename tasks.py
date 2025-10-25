"""
Small helper wrapper for task operations.
Keeps DB calls in one place and returns nice structures for the UI.
"""
import db

def get_tasks_rows(username):
    """
    Returns rows in the UI-friendly format:
    [(title, start_date, due_date, status), ...]
    """
    return db.get_tasks(username) or []

def add_new_task(user_id, username, title, start_date, due_date, status="In Progress"):
    # Basic validation can be extended
    if not title:
        return False
    return db.add_task(user_id, username, title, start_date, due_date, status)

def delete_task_by_title(username, title):
    return db.delete_task(username, title)
