import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
import db
import auth

def open_dashboard(username, app):
    for widget in app.winfo_children():
        widget.destroy()

    app.title(f"Work Tracker - {username}")

    # Configure app grid
    app.columnconfigure(0, weight=0)  # sidebar fixed width
    app.columnconfigure(1, weight=1)  # main content flexible
    app.rowconfigure(0, weight=1)

    # Sidebar menu frame
    sidebar = ttk.Frame(app, padding=10, bootstyle="secondary")
    sidebar.grid(row=0, column=0, sticky="ns")
    sidebar.grid_propagate(False)
    sidebar.config(width=180)

    # Content frame (dynamic content area)
    content = ttk.Frame(app, padding=20)
    content.grid(row=0, column=1, sticky="nsew")

    # Sidebar buttons without icons
    ttk.Label(sidebar, text=f"Hello, {username}", font=("Segoe UI", 12, "bold")).pack(pady=(0, 20))

    ttk.Button(sidebar, text="Overview", command=lambda: show_welcome(username, content)).pack(fill="x", pady=5)
    ttk.Button(sidebar, text="Task", command=lambda: show_tasks(username, content)).pack(fill="x", pady=5)
    ttk.Button(sidebar, text="Timer", command=lambda: show_timer(username, content)).pack(fill="x", pady=5)
    ttk.Button(sidebar, text="Analytic", command=lambda: show_analytic(username, content)).pack(fill="x", pady=5)
    ttk.Button(sidebar, text="Settings", command=lambda: show_settings(username, content)).pack(fill="x", pady=5)
    ttk.Button(sidebar, text="Logout", bootstyle="danger-outline", command=lambda: logout_action(app)).pack(fill="x", pady=20)

    # Show welcome message initially
    show_welcome(username, content)

def clear_content(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_welcome(username, frame):
    clear_content(frame)
    ttk.Label(frame, text=f"Welcome to Work Tracker, {username}!", font=("Segoe UI", 16, "bold")).pack(expand=True)

def show_tasks(username, frame):
    clear_content(frame)
    ttk.Label(frame, text="Your Tasks", font=("Segoe UI", 14, "bold")).pack(pady=10)

    tasks = db.get_tasks(username)
    columns = ["Title", "Start Date", "Due Date"]

    table = Tableview(master=frame, coldata=columns, rowdata=tasks, paginated=False, searchable=True)
    table.pack(fill="both", expand=True, pady=10)

def show_timer(username, frame):
    clear_content(frame)
    ttk.Label(frame, text="Timer - Coming Soon!", font=("Segoe UI", 14, "bold")).pack(expand=True)

def show_analytic(username, frame):
    clear_content(frame)
    ttk.Label(frame, text="Analytic - Coming Soon!", font=("Segoe UI", 14, "bold")).pack(expand=True)

def show_settings(username, frame):
    clear_content(frame)
    ttk.Label(frame, text="Settings - Coming Soon!", font=("Segoe UI", 14, "bold")).pack(expand=True)

def logout_action(app):
    if auth.logout():
        Messagebox.show_info("Logged out successfully.")
        for widget in app.winfo_children():
            widget.destroy()
        from login import LoginWindow
        LoginWindow(app)
    else:
        Messagebox.show_error("Logout failed.")
