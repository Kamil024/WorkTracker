import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import tkinter as tk
import db
from auth import logout
from datetime import datetime
from settings import load_theme_preference

def open_dashboard(username, app):
    theme = load_theme_preference()  # Load saved theme ("light" or "dark")

    # Define colors based on theme
    if theme == "dark":
        bg_color = "#2c3e50"
        panel_color = "#34495e"
        text_color = "white"
        label_text_color = "white"
        entry_bg_color = "#2c3e50"
        entry_fg_color = "white"
        button_fg_color = "#2980b9"
        button_hover_color = "#3498db"
        danger_fg_color = "#c0392b"
        danger_hover_color = "#e74c3c"
        done_fg_color = "#27ae60"
        done_hover_color = "#2ecc71"
    else:
        bg_color = "#ecf0f1"
        panel_color = "white"
        text_color = "#2c3e50"
        label_text_color = "#2c3e50"
        entry_bg_color = "white"
        entry_fg_color = "black"
        button_fg_color = "#2980b9"
        button_hover_color = "#3498db"
        danger_fg_color = "#c0392b"
        danger_hover_color = "#e74c3c"
        done_fg_color = "#27ae60"
        done_hover_color = "#2ecc71"

    for w in app.winfo_children():
        w.destroy()

    app.configure(fg_color=bg_color)
    app.title(f"{username}'s Dashboard")
    app.geometry("1200x700")

    # Add this attribute to track the history window
    if not hasattr(app, "history_window"):
        app.history_window = None

    # LEFT PANEL
    left = ctk.CTkFrame(app, width=350, fg_color=panel_color, corner_radius=12)
    left.pack(side="left", fill="y", padx=16, pady=16)

    ctk.CTkLabel(
        left, text=f"👋 Welcome, {username}!", font=("Arial", 18, "bold"), text_color=label_text_color
    ).pack(pady=(20, 16))

    title_entry = ctk.CTkEntry(
        left,
        placeholder_text="Task title / description",
        height=35,
        fg_color=entry_bg_color,
        text_color=entry_fg_color,
    )
    title_entry.pack(fill="x", padx=12, pady=(0, 12))

    ctk.CTkLabel(left, text="Start Date:", text_color=label_text_color).pack(anchor="w", padx=12)
    start_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    start_entry.pack(fill="x", padx=12, pady=(0, 10))

    ctk.CTkLabel(left, text="Due Date:", text_color=label_text_color).pack(anchor="w", padx=12)
    due_entry = DateEntry(left, date_pattern="yyyy-mm-dd")
    due_entry.pack(fill="x", padx=12, pady=(0, 16))

    def load_tasks():
        for w in tasks_frame.winfo_children():
            w.destroy()

        today = datetime.today().date()
        for task_id, title, start, due, completed in db.get_tasks(username):
            try:
                due_dt = datetime.strptime(due, "%Y-%m-%d").date()
            except Exception:
                due_dt = today

            if due_dt < today:
                color = "red"
            elif due_dt == today:
                color = "orange"
            else:
                color = text_color

            row = ctk.CTkFrame(tasks_frame, fg_color=panel_color)
            row.pack(fill="x", padx=6, pady=4)

            ctk.CTkLabel(row, text=title, text_color=color, anchor="w").pack(
                side="left", fill="x", expand=True, padx=6
            )
            ctk.CTkLabel(row, text=f"Due: {due}", text_color=color).pack(side="left", padx=6)

            ctk.CTkButton(
                row,
                text="Done",
                width=60,
                fg_color=done_fg_color,
                hover_color=done_hover_color,
                command=lambda tid=task_id: (db.update_task_completion(tid, 1), load_tasks()),
            ).pack(side="right", padx=4)
            ctk.CTkButton(
                row,
                text="Delete",
                width=60,
                fg_color=danger_fg_color,
                hover_color=danger_hover_color,
                command=lambda tid=task_id: (db.delete_task(tid), load_tasks()),
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
        hist.configure(fg_color=panel_color)

        # Container for tasks
        container = ctk.CTkScrollableFrame(hist, fg_color=panel_color)
        container.pack(fill="both", expand=True, padx=12, pady=12)

        # Store task checkboxes
        task_vars = {}
        checkboxes = []

        # Load completed tasks
        completed = db.get_completed_tasks(user)
        if not completed:
            tk.Label(container, text="No completed tasks yet.", fg="gray").pack(pady=8)
        else:
            for tid, title, start, due, _ in completed:
                var = tk.BooleanVar(value=False)
                cb = tk.Checkbutton(
                    container,
                    text=f"{title} | Start: {start} | Due: {due}",
                    variable=var,
                    onvalue=True,
                    offvalue=False,
                    anchor="w",
                    bg=panel_color,
                    fg=label_text_color,
                    selectcolor=panel_color,
                    activebackground=panel_color,
                    activeforeground=label_text_color,
                )
                cb.pack(fill="x", anchor="w", pady=2)
                task_vars[tid] = var
                checkboxes.append(cb)

        def delete_selected():
            to_delete = [tid for tid, var in task_vars.items() if var.get()]
            if not to_delete:
                messagebox.showwarning("No selection", "Please select at least one task to delete.")
                return
            for tid in to_delete:
                db.delete_task(tid)
            hist.destroy()
            open_history(user)  # refresh after delete

        delete_btn = ctk.CTkButton(
            hist,
            text="🗑 Delete Selected Task(s)",
            fg_color=danger_fg_color,
            hover_color=danger_hover_color,
            command=delete_selected,
        )
        delete_btn.pack(pady=8)

        def on_close():
            app.history_window = None
            hist.destroy()

        hist.protocol("WM_DELETE_WINDOW", on_close)

    ctk.CTkButton(
        left,
        text="➕ Add Task",
        fg_color=button_fg_color,
        hover_color=button_hover_color,
        height=35,
        command=add_task,
    ).pack(fill="x", padx=12, pady=(0, 12))

    ctk.CTkButton(
        left,
        text="📜 History",
        fg_color="#8e44ad",
        hover_color="#9b59b6",
        height=35,
        command=lambda: open_history(username),
    ).pack(fill="x", padx=12, pady=(0, 10))

    def from_login():
        from login import show_startup

        show_startup(app)

    ctk.CTkButton(
        left,
        text="🚪 Logout",
        fg_color=danger_fg_color,
        hover_color=danger_hover_color,
        height=35,
        command=lambda: (logout(), from_login()),
    ).pack(fill="x", padx=12, pady=(10, 0))

    # RIGHT PANEL
    right = ctk.CTkFrame(app, fg_color=panel_color, corner_radius=12)
    right.pack(side="right", fill="both", expand=True, padx=16, pady=16)

    ctk.CTkLabel(
        right, text="📅 Active Tasks", font=("Arial", 18, "bold"), text_color=label_text_color
    ).pack(anchor="w", pady=(16, 8), padx=12)

    tasks_frame = ctk.CTkScrollableFrame(right, fg_color=panel_color)
    tasks_frame.pack(fill="both", expand=True, padx=12, pady=12)

    # Initial load
    load_tasks()
