"""
Wrapper around db task operations used by the UI.
Keeps backward-compatible function signatures.
"""
import db

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


def delete_task_by_title(username, title):
    return db.delete_task(username, title)


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

        # ---------- Case A: explicit task_id path ----------
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

        # ---------- Case B: dashboard-style ----------
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
