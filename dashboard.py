import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
import db
import auth


def open_dashboard(username, app):
    """Opens the main dashboard."""
    for widget in app.winfo_children():
        widget.destroy()

    app.title(f"Work Tracker - {username}")

    frame = ttk.Frame(app, padding=20)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text=f"Welcome, {username}!", font=("Helvetica", 16, "bold")).pack(pady=10)

    ttk.Button(frame, text="View Tasks", command=lambda: show_tasks(username, frame)).pack(pady=5)
    ttk.Button(frame, text="Add Task", command=lambda: add_task_form(username, frame)).pack(pady=5)
    ttk.Button(frame, text="Logout", command=lambda: logout_action(app)).pack(pady=5)


def show_tasks(username, frame):
    """Display all tasks."""
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text="Your Tasks", font=("Helvetica", 14, "bold")).pack(pady=10)

    tasks = db.get_tasks(username)
    columns = ["Title", "Start Date", "Due Date"]
    table = Tableview(master=frame, coldata=columns, rowdata=tasks, paginated=False, searchable=True)
    table.pack(fill="both", expand=True, pady=10)

    ttk.Button(frame, text="Back", command=lambda: open_dashboard(username, frame.master)).pack(pady=5)


def add_task_form(username, frame):
    """Form to add a new task."""
    for widget in frame.winfo_children():
        widget.destroy()

    ttk.Label(frame, text="Add New Task", font=("Helvetica", 14, "bold")).pack(pady=10)

    title_var = ttk.StringVar()
    start_var = ttk.StringVar()
    due_var = ttk.StringVar()

    ttk.Label(frame, text="Title:").pack(pady=5)
    ttk.Entry(frame, textvariable=title_var).pack(pady=5)
    ttk.Label(frame, text="Start Date (YYYY-MM-DD):").pack(pady=5)
    ttk.Entry(frame, textvariable=start_var).pack(pady=5)
    ttk.Label(frame, text="Due Date (YYYY-MM-DD):").pack(pady=5)
    ttk.Entry(frame, textvariable=due_var).pack(pady=5)

    def submit_task():
        title = title_var.get().strip()
        start = start_var.get().strip()
        due = due_var.get().strip()
        if not title:
            Messagebox.show_warning("Please enter a task title.")
            return

        user = db.get_user(username)
        user_id = user[0] if user else None
        if db.add_task(user_id, username, title, start, due):
            Messagebox.show_info("Task added successfully!")
            open_dashboard(username, frame.master)
        else:
            Messagebox.show_error("Failed to add task.")

    ttk.Button(frame, text="Add Task", command=submit_task).pack(pady=10)
    ttk.Button(frame, text="Back", command=lambda: open_dashboard(username, frame.master)).pack(pady=5)


def logout_action(app):
    if auth.logout():
        Messagebox.show_info("Logged out successfully.")
        app.destroy()
        from login import LoginWindow
        LoginWindow()
    else:
        Messagebox.show_error("Logout failed.")
