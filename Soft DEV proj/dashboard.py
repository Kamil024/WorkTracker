import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import db
from auth import logout
from datetime import datetime

_history_win = None  # single instance for history window

def open_dashboard(username, app):
    global _history_win

    # Clear previous widgets
    for w in app.winfo_children():
        w.destroy()
    app.title(f"{username}'s Dashboard")
    app.geometry("1200x700")

    # ===== LEFT FRAME: Create Task =====
    left = ctk.CTkFrame(app, width=360)
    left.pack(side="left", fill="y", padx=16, pady=16)

    ctk.CTkLabel(left, text=f"Welcome, {username}!", font=("Arial", 18, "bold")).pack(pady=(0,12))

    title_entry = ctk.CTkEntry(left, placeholder_text="Task title / description")
    title_entry.pack(fill="x", padx=8, pady=(0,10))

    ctk.CTkLabel(left, text="Start Date:").pack(anchor="w", padx=8)
    start_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    start_entry.pack(fill="x", padx=8, pady=(0,10))

    ctk.CTkLabel(left, text="Due Date:").pack(anchor="w", padx=8)
    due_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    due_entry.pack(fill="x", padx=8, pady=(0,14))

    def add_task():
        title = title_entry.get().strip()
        start_date = start_entry.get()
        due_date = due_entry.get()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task title.")
            return
        db.add_task(username, title, start_date, due_date)
        title_entry.delete(0,"end")
        load_tasks()

    ctk.CTkButton(left, text="Add Task", command=add_task).pack(fill="x", padx=8, pady=(0,10))

    # Logout button
    def do_logout():
        logout()
        from login import show_startup  # import here to avoid circular import
        show_startup(app)

    ctk.CTkButton(left, text="Logout", command=do_logout).pack(fill="x", padx=8, pady=(20,0))

    # History button
    def open_history():
        global _history_win
        if _history_win is not None and _history_win.winfo_exists():
            _history_win.lift()
            return

        _history_win = ctk.CTkToplevel(app)
        _history_win.title("Task History")
        _history_win.geometry("700x500")

        def on_close():
            global _history_win
            _history_win.destroy()
            _history_win = None

        _history_win.protocol("WM_DELETE_WINDOW", on_close)

        hist_frame = ctk.CTkScrollableFrame(_history_win)
        hist_frame.pack(fill="both", expand=True, padx=12, pady=12)

        completed = db.get_completed_tasks(username)
        if not completed:
            ctk.CTkLabel(hist_frame, text="No completed tasks yet.").pack(pady=8)
        else:
            for row in completed:
                task_id, title, start, due, _ = row
                ctk.CTkLabel(
                    hist_frame,
                    text=f"✅ {title}\nStart: {start}   Due: {due}",
                    anchor="w",
                    justify="left",
                    wraplength=650
                ).pack(fill="x", padx=6, pady=4)

    ctk.CTkButton(left, text="Show History", command=open_history).pack(fill="x", padx=8, pady=(10,0))

    # ===== RIGHT FRAME: Active Tasks =====
    right = ctk.CTkFrame(app)
    right.pack(side="right", fill="both", expand=True, padx=16, pady=16)

    ctk.CTkLabel(right, text="Active Tasks", font=("Arial", 18, "bold")).pack(anchor="w", pady=(0,8), padx=8)

    tasks_frame = ctk.CTkScrollableFrame(right)
    tasks_frame.pack(fill="both", expand=True, padx=8, pady=8)

    task_labels = []

    def compute_wrap():
        avail = max(tasks_frame.winfo_width(), 400)
        return max(300, avail - 240)

    def delete_task(task_id):
        db.delete_task(task_id)
        load_tasks()

    def mark_done(task_id):
        db.update_task_completion(task_id, 1)
        load_tasks()

    def load_tasks():
        nonlocal task_labels
        task_labels = []

        for w in tasks_frame.winfo_children():
            w.destroy()

        rows = db.get_tasks(username)
        today = datetime.today().date()

        for row in rows:
            task_id, title, start, due, _ = row
            due_dt = datetime.strptime(due, "%Y-%m-%d").date()

            task_row = ctk.CTkFrame(tasks_frame, fg_color="transparent")
            task_row.pack(fill="x", padx=6, pady=4)

            # Color-code overdue/urgent tasks
            if due_dt < today:
                text_color = "red"
            elif due_dt == today:
                text_color = "orange"
            else:
                text_color = None  # default

            # Title left
            left_lbl = ctk.CTkLabel(task_row, text=title, anchor="w", text_color=text_color)
            left_lbl.pack(side="left", fill="x", expand=True, padx=5)

            # Due right
            right_lbl = ctk.CTkLabel(task_row, text=f"Due: {due}", anchor="e", text_color=text_color)
            right_lbl.pack(side="right", padx=5)

            # Buttons
            ctk.CTkButton(task_row, text="Done", width=80, fg_color="green", command=lambda tid=task_id: mark_done(tid)).pack(side="right", padx=4)
            ctk.CTkButton(task_row, text="Delete", width=80, fg_color="red", command=lambda tid=task_id: delete_task(tid)).pack(side="right", padx=4)

            task_labels.append(left_lbl)

    app.bind("<Configure>", lambda e: [lbl.configure(wraplength=max(tasks_frame.winfo_width()-240,300)) for lbl in task_labels])
    load_tasks()
