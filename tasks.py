"""
Wrapper around db task operations used by the UI.
Keeps backward-compatible function signatures.
Adds safe delete and auto-cleanup helpers.
"""
import db
import datetime
import sqlite3

def get_tasks_rows(username):
    """
    Returns rows in the UI-friendly format.
    Legacy: [(title, start_date, due_date, status), ...]
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

    try:
        return db.add_task(user_id, username, title, start_date, due_date, status,
                           description, priority, category, estimated_minutes)
    except Exception as e:
        print(f"[tasks.py] add_new_task error: {e}")
        return False



# Deletion helpers

def get_task_id_by_username_title(username, title, start_date=None):
    """
    Find the most relevant task id for the given username + title.
    If start_date is provided, prefer exact match on start_date.
    Returns task id int or None.
    """
    try:
        with db.connect() as conn:
            cur = conn.cursor()
            if start_date:
                cur.execute("""
                    SELECT id FROM tasks
                    WHERE username = ? AND title = ? AND start_date = ?
                    ORDER BY id DESC LIMIT 1
                """, (username, title, start_date))
                r = cur.fetchone()
                if r:
                    return r[0]
            # fallback: match by username + title only
            cur.execute("""
                SELECT id FROM tasks
                WHERE username = ? AND title = ?
                ORDER BY id DESC LIMIT 1
            """, (username, title))
            r = cur.fetchone()
            if r:
                return r[0]
    except Exception as e:
        print(f"[tasks.py] get_task_id_by_username_title error: {e}")
    return None

def delete_task_by_title(username, title):
    """
    Backwards-compatible delete by username+title.
    Returns True on success, False otherwise.
    """
    try:
        # if db exposes delete_task, use it first (backwards compatibility)
        try:
            res = db.delete_task(username, title)
            # Some older db.delete_task may return None/True/False or dict.
            if isinstance(res, dict):
                return res.get("success", False)
            if isinstance(res, bool):
                return res
            # if it returned something else, fallthrough to SQL delete
        except AttributeError:
            # db.delete_task not present
            pass

        tid = get_task_id_by_username_title(username, title)
        if tid is None:
            print(f"[tasks.py] delete_task_by_title: no task found for user={username}, title={title}")
            return False
        return delete_task_by_id(tid, username=username)
    except Exception as e:
        print(f"[tasks.py] delete_task_by_title error: {e}")
        return False

def delete_task_by_id(task_id, username=None):
    """
    Delete a task by its id.
    If username is provided, ensure the task belongs to that user.
    Returns True on success, False otherwise.
    """
    try:
        with db.connect() as conn:
            cur = conn.cursor()
            if username:
                cur.execute("DELETE FROM tasks WHERE id = ? AND username = ?", (task_id, username))
            else:
                cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()
            if cur.rowcount > 0:
                print(f"[tasks.py] Deleted task id={task_id} (user={username})")
                return True
            else:
                print(f"[tasks.py] delete_task_by_id: no rows deleted for id={task_id} (user={username})")
                return False
    except Exception as e:
        print(f"[tasks.py] delete_task_by_id error: {e}")
        return False

def safe_delete_task(username, title):
    """
    Safe deletion wrapper used by UI code: finds the most relevant task for the user/title
    and deletes it. Returns True/False.
    This function does not prompt the user; the UI module should prompt before calling.
    """
    try:
        tid = get_task_id_by_username_title(username, title)
        if not tid:
            print(f"[tasks.py] safe_delete_task: could not find task for user={username}, title={title}")
            return False
        return delete_task_by_id(tid, username=username)
    except Exception as e:
        print(f"[tasks.py] safe_delete_task error: {e}")
        return False

def auto_delete_overdue(days=30):
    """
    Auto-cleanup: delete tasks with due_date older than `days` (relative to today)
    and not marked as Completed.
    Returns a dict { "deleted": n, "success": True/False }.
    NOTE: This is aggressive — call only from admin/maintenance code or with user confirmation.
    """
    try:
        # compute cutoff date as YYYY-MM-DD
        cutoff = (datetime.date.today() - datetime.timedelta(days=int(days))).isoformat()
        with db.connect() as conn:
            cur = conn.cursor()
            # Only delete tasks that have a non-empty due_date and where due_date < cutoff
            # and status is not 'Completed'
            cur.execute("""
                DELETE FROM tasks
                WHERE due_date IS NOT NULL AND due_date != ''
                  AND date(due_date) < date(?)
                  AND (status IS NULL OR LOWER(status) != 'completed')
            """, (cutoff,))
            deleted = cur.rowcount
            conn.commit()
        print(f"[tasks.py] auto_delete_overdue: deleted {deleted} tasks older than {cutoff}")
        return {"deleted": deleted, "success": True}
    except Exception as e:
        print(f"[tasks.py] auto_delete_overdue error: {e}")
        return {"deleted": 0, "success": False, "error": str(e)}



# Existing flexible updater (kept as-is)

def update_task(*args, **kwargs):
    """
    Flexible update function to handle multiple caller patterns.

    Supported caller patterns:

    A) Direct update by id:
       update_task(task_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes)

    B) Dashboard-style:
       update_task(user_id, username, title_old, new_title, new_start, new_due, new_status,
                   description=..., priority=..., category=..., estimated_minutes=...)

    The function will find the task id if necessary, update, commit, and return True/False.
    """
    try:
        # Extract optional keyword args
        description = kwargs.get("description", None)
        priority = kwargs.get("priority", None)
        category  = kwargs.get("category", None)
        estimated_minutes = kwargs.get("estimated_minutes", None)

        # Normalize estimated_minutes
        try:
            if estimated_minutes is not None and estimated_minutes != "":
                estimated_minutes = int(estimated_minutes)
            else:
                estimated_minutes = 0
        except Exception:
            estimated_minutes = 0

        #  Case A: explicit task_id path 
        if len(args) >= 6:
            # try interpret args[0] as task_id and args[1] as username
            possible_id = args[0]
            username_arg = args[1] if len(args) > 1 else None
            try:
                tid = int(possible_id)
                with db.connect() as conn:
                    cur = conn.cursor()
                    cur.execute("SELECT id FROM tasks WHERE id = ? AND username = ?", (tid, username_arg))
                    found = cur.fetchone()
                    if found:
                        # Extract fields from positional args or kwargs
                        title = args[2] if len(args) > 2 else kwargs.get("title", "")
                        start_date = args[3] if len(args) > 3 else kwargs.get("start_date", "")
                        due_date = args[4] if len(args) > 4 else kwargs.get("due_date", "")
                        status = args[5] if len(args) > 5 else kwargs.get("status", "In Progress")
                        if description is None:
                            description = args[6] if len(args) > 6 else None
                        if priority is None:
                            priority = args[7] if len(args) > 7 else None
                        if category is None:
                            category = args[8] if len(args) > 8 else None
                        if estimated_minutes is None and len(args) > 9:
                            try:
                                estimated_minutes = int(args[9])
                            except Exception:
                                estimated_minutes = 0

                        # Safety defaults
                        title = title or ""
                        start_date = start_date or ""
                        due_date = due_date or ""
                        status = status or "In Progress"
                        estimated_minutes = int(estimated_minutes or 0)

                        cur.execute("""
                            UPDATE tasks
                            SET title = ?, start_date = ?, due_date = ?, status = ?, 
                                description = ?, priority = ?, category = ?, estimated_minutes = ?
                            WHERE id = ? AND username = ?
                        """, (title, start_date, due_date, status, description, priority, category, estimated_minutes, tid, username_arg))
                        conn.commit()
                        if cur.rowcount > 0:
                            print(f"[tasks.py] Updated task id={tid} for user={username_arg}")
                            return True
                        else:
                            print(f"[tasks.py] No rows updated for id={tid} and user={username_arg}")
                            return False
            except ValueError:
                # not an int -> fallthrough to dashboard-style matching
                pass

        #  Case B: dashboard-style 
        # args: (user_id, username, title_old, new_title, new_start, new_due, new_status)
        if len(args) >= 7:
            user_id = args[0]
            username = args[1]
            title_old = args[2]
            new_title = args[3]
            new_start = args[4]
            new_due = args[5]
            new_status = args[6]

            # prefer kwargs if provided
            if "description" in kwargs:
                description = kwargs.get("description")
            if "priority" in kwargs:
                priority = kwargs.get("priority")
            if "category" in kwargs:
                category = kwargs.get("category")
            if "estimated_minutes" in kwargs:
                try:
                    estimated_minutes = int(kwargs.get("estimated_minutes", 0))
                except Exception:
                    estimated_minutes = 0

            with db.connect() as conn:
                cur = conn.cursor()
                # First try exact match with start_date
                cur.execute("""
                    SELECT id FROM tasks
                    WHERE username = ? AND title = ? AND start_date = ?
                    ORDER BY id DESC LIMIT 1
                """, (username, title_old, new_start))
                row = cur.fetchone()
                if not row:
                    # fallback: match by username + title only
                    cur.execute("""
                        SELECT id FROM tasks
                        WHERE username = ? AND title = ?
                        ORDER BY id DESC LIMIT 1
                    """, (username, title_old))
                    row = cur.fetchone()
                if not row:
                    print(f"[tasks.py] Could not find task to update for user={username}, title_old={title_old}")
                    return False

                task_id = row[0]

                # final safety defaults
                new_title = new_title or title_old
                new_start = new_start or ""
                new_due = new_due or ""
                new_status = new_status or "In Progress"
                estimated_minutes = int(estimated_minutes or 0)

                cur.execute("""
                    UPDATE tasks
                    SET title = ?, start_date = ?, due_date = ?, status = ?, 
                        description = ?, priority = ?, category = ?, estimated_minutes = ?
                    WHERE id = ? AND username = ?
                """, (new_title, new_start, new_due, new_status, description, priority, category, estimated_minutes, task_id, username))
                conn.commit()
                if cur.rowcount > 0:
                    print(f"[tasks.py] ✅ Task (id={task_id}) updated for user={username}")
                    return True
                else:
                    print(f"[tasks.py] ⚠️ Update executed but rowcount==0 (id={task_id}, user={username})")
                    return False

        # unsupported call pattern
        print("[tasks.py] update_task called with unsupported arguments.")
        return False

    except Exception as e:
        print(f"[tasks.py] update_task error: {e}")
        return False
