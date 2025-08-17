import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import db
from auth import logout
from datetime import datetime

def open_dashboard(username, app):
    for w in app.winfo_children():
        w.destroy()

    app.configure(fg_color="#ecf0f1")
    app.title(f"{username}'s Dashboard")
    app.geometry("1200x700")

    # Add this attribute to track the history window
    if not hasattr(app, "history_window"):
        app.history_window = None

    # LEFT PANEL
    left = ctk.CTkFrame(app, width=350, fg_color="white", corner_radius=12)
    left.pack(side="left", fill="y", padx=16, pady=16)

    ctk.CTkLabel(
        left, text=f"👋 Welcome, {username}!", font=("Arial", 18, "bold"), text_color="#2c3e50"
    ).pack(pady=(20, 16))

    title_entry = ctk.CTkEntry(left, placeholder_text="Task title / description", height=35)
    title_entry.pack(fill="x", padx=12, pady=(0, 12))

    ctk.CTkLabel(left, text="Start Date:", text_color="#7f8c8d").pack(anchor="w", padx=12)
    start_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    start_entry.pack(fill="x", padx=12, pady=(0, 10))

    ctk.CTkLabel(left, text="Due Date:", text_color="#7f8c8d").pack(anchor="w", padx=12)
    due_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    due_entry.pack(fill="x", padx=12, pady=(0, 16))

    def load_tasks():
        for w in tasks_frame.winfo_children():
            w.destroy()

        today = datetime.today().date()
        for task_id, title, start, due, completed in db.get_tasks(username):
            due_dt = datetime.strptime(due, "%Y-%m-%d").date()
            if due_dt < today:
                color = "red"
            elif due_dt == today:
                color = "orange"
            else:
                color = "#2c3e50"

            row = ctk.CTkFrame(tasks_frame, fg_color="white")
            row.pack(fill="x", padx=6, pady=4)

            ctk.CTkLabel(row, text=title, text_color=color, anchor="w").pack(side="left", fill="x", expand=True, padx=6)
            ctk.CTkLabel(row, text=f"Due: {due}", text_color=color).pack(side="left", padx=6)

            ctk.CTkButton(
                row, text="Done", width=60, fg_color="#27ae60", hover_color="#2ecc71",
                command=lambda tid=task_id: (db.update_task_completion(tid, 1), load_tasks())
            ).pack(side="right", padx=4)
            ctk.CTkButton(
                row, text="Delete", width=60, fg_color="#c0392b", hover_color="#e74c3c",
                command=lambda tid=task_id: (db.delete_task(tid), load_tasks())
            ).pack(side="right", padx=4)

    def add_task():
        title = title_entry.get().strip()
        if not title:
            messagebox.showwarning("Missing title", "Please enter a task title.")
            return
        db.add_task(username, title, start_entry.get(), due_entry.get())
        title_entry.delete(0, "end")
        load_tasks()

    def open_history(user):
        # Prevent multiple history windows
        if app.history_window is not None and app.history_window.winfo_exists():
            app.history_window.lift()
            return

        hist = ctk.CTkToplevel(app)
        app.history_window = hist
        hist.title("Task History")
        hist.geometry("700x500")
        hist.configure(fg_color="white")

        hist_frame = ctk.CTkScrollableFrame(hist)
        hist_frame.pack(fill="both", expand=True, padx=12, pady=12)

        completed = db.get_completed_tasks(user)
        if not completed:
            ctk.CTkLabel(hist_frame, text="No completed tasks yet.").pack(pady=8)
        else:
            for _, title, start, due, _ in completed:
                ctk.CTkLabel(hist_frame, text=f"✅ {title}\nStart: {start}   Due: {due}",
                             anchor="w", justify="left").pack(fill="x", padx=6, pady=4)

        def on_close():
            app.history_window = None
            hist.destroy()
        hist.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkButton(
        left, text="➕ Add Task", fg_color="#2980b9", hover_color="#3498db",
        height=35, command=add_task
    ).pack(fill="x", padx=12, pady=(0, 12))

    ctk.CTkButton(
        left, text="📜 History", fg_color="#8e44ad", hover_color="#9b59b6",
        height=35, command=lambda: open_history(username)
    ).pack(fill="x", padx=12, pady=(0, 10))

    def from_login():
        from login import show_startup
        show_startup(app)

    ctk.CTkButton(
        left, text="🚪 Logout", fg_color="#c0392b", hover_color="#e74c3c",
        height=35, command=lambda: (logout(), from_login())
    ).pack(fill="x", padx=12, pady=(10, 0))

    # RIGHT PANEL
    right = ctk.CTkFrame(app, fg_color="white", corner_radius=12)
    right.pack(side="right", fill="both", expand=True, padx=16, pady=16)

    ctk.CTkLabel(
        right, text="📅 Active Tasks", font=("Arial", 18, "bold"), text_color="#2c3e50"
    ).pack(anchor="w", pady=(16, 8), padx=12)

    tasks_frame = ctk.CTkScrollableFrame(right)
    tasks_frame.pack(fill="both", expand=True, padx=12, pady=12)

    # Initial load
    load_tasks()