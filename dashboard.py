import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
import db
import auth
from datetime import datetime


def open_dashboard(user, root):
    username = user["username"] if isinstance(user, dict) and "username" in user else str(user)

    for w in root.winfo_children():
        w.destroy()

    root.title(f"WorkTracker Pro — {username}")
    root.geometry("1280x780")
    root.minsize(1000, 600)

    # Unbind Enter key from login
    root.unbind("<Return>")

    style = ttk.Style("litera")

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)
    container.columnconfigure(0, weight=0)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(1, weight=1)

    # --- Topbar ---
    topbar = ttk.Frame(container, padding=(18, 10), bootstyle="light")
    topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
    topbar.columnconfigure(0, weight=1)
    ttk.Label(topbar, text="WorkTracker Pro", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")

    # --- Right area ---
    right_area = ttk.Frame(topbar)
    right_area.grid(row=0, column=1, sticky="e")
    ttk.Button(
        right_area,
        text="🚪 Logout",
        bootstyle="danger",
        command=lambda: logout_action(root)
    ).pack(side="left", padx=8)
    ttk.Label(right_area, text=username[0].upper(),
              bootstyle="primary-inverse",
              width=3, anchor="center").pack(side="left", padx=(6, 0))

    # --- Layout ---
    layout = ttk.Frame(container)
    layout.grid(row=1, column=0, columnspan=2, sticky="nsew")
    layout.columnconfigure(1, weight=1)
    layout.rowconfigure(0, weight=1)

    # --- Sidebar ---
    sidebar_width = tk.IntVar(value=220)
    sidebar = ttk.Frame(layout, padding=(12, 18), bootstyle="light")
    sidebar.grid(row=0, column=0, sticky="nsw")
    sidebar.config(width=sidebar_width.get())
    sidebar.pack_propagate(False)

    # Collapsible toggle
    def toggle_sidebar():
        if sidebar_width.get() > 60:
            sidebar_width.set(60)
            for child in sidebar.winfo_children():
                if isinstance(child, ttk.Button) and hasattr(child, "text_label"):
                    child.text_label.pack_forget()
        else:
            sidebar_width.set(220)
            for child in sidebar.winfo_children():
                if isinstance(child, ttk.Button) and hasattr(child, "text_label"):
                    child.text_label.pack(side="left", padx=(10, 0))
        sidebar.config(width=sidebar_width.get())

    toggle_btn = ttk.Button(sidebar, text="☰", bootstyle="secondary", command=toggle_sidebar)
    toggle_btn.pack(anchor="w", pady=(0, 12))

    def nav_btn(icon, text, cmd, active=False):
        bs = "dark" if active else "light"
        btn = ttk.Button(sidebar, bootstyle=f"{bs}-outline", command=cmd)
        btn.pack(fill="x", pady=6, ipady=6)
        frame = ttk.Frame(btn)
        frame.pack(fill="x")
        ttk.Label(frame, text=icon, font=("Segoe UI", 11)).pack(side="left", padx=(8, 0))
        btn.text_label = ttk.Label(frame, text=text, font=("Segoe UI", 10))
        btn.text_label.pack(side="left", padx=(10, 0))
        return btn

    # --- Content ---
    content = ttk.Frame(layout, padding=20)
    content.grid(row=0, column=1, sticky="nsew")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(2, weight=1)

    # --- Navigation buttons ---
    nav_btn("🏠", "Overview", lambda: show_welcome(username, content), active=True)
    nav_btn("📝", "Tasks", lambda: show_tasks(username, content))
    nav_btn("📊", "Analytics", lambda: show_analytic(username, content))
    nav_btn("⚙️", "Settings", lambda: show_settings(username, content))

    show_welcome(username, content)


def clear_frame(f):
    for w in f.winfo_children():
        w.destroy()


def card(parent, title, value, icon=None):
    f = ttk.Frame(parent, padding=12, bootstyle="light")
    f.pack(side="left", expand=True, fill="both", padx=8)
    ttk.Label(f, text=title, font=("Segoe UI", 9)).pack(anchor="w")
    ttk.Label(f, text=value, font=("Segoe UI", 18, "bold")).pack(anchor="center", pady=(8, 0))
    if icon:
        ttk.Label(f, text=icon, font=("Segoe UI Emoji", 16)).pack(anchor="e")


def show_welcome(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text=f"Welcome back, {username}!", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Your productivity overview for today.", font=("Segoe UI", 10),
              foreground="#6c757d").pack(anchor="w", pady=(4, 10))
    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill="x", pady=(18, 12))
    card(stats_frame, "Completed", "5", icon="✅")
    card(stats_frame, "In Progress", "2", icon="🔁")
    card(stats_frame, "Overdue", "1", icon="⚠️")
    card(stats_frame, "Focus Time", "120m", icon="⏱")
    ttk.Label(frame, text="Recent Tasks", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 6))
    tasks = db.get_tasks(username)
    if not tasks:
        ttk.Label(frame, text="No recent tasks. Start one now!", foreground="#888").pack(anchor="w")
    else:
        for t in tasks[:5]:
            ttk.Label(frame, text=f"• {t[0]} (Due: {t[2]})", font=("Segoe UI", 10)).pack(anchor="w")


# --- Tasks with Add + Timer ---
def show_tasks(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Tasks", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))

    # Add Task Button
    ttk.Button(frame, text="➕ Add Task", bootstyle="success", command=lambda: open_add_task_modal(username, frame)).pack(anchor="e", pady=(0, 8))

    rows = db.get_tasks(username)
    columns = ["Title", "Start Date", "Due Date"]
    table = Tableview(master=frame, coldata=columns, rowdata=rows, paginated=False, searchable=True)
    table.pack(fill="both", expand=True)

    # --- Timer ---
    timer_frame = ttk.Frame(frame, padding=10)
    timer_frame.pack(fill="x", pady=(20, 0))
    ttk.Label(timer_frame, text="Focus Timer", font=("Segoe UI", 12, "bold")).pack(anchor="w")

    time_var = tk.StringVar(value="00:00:00")
    ttk.Label(timer_frame, textvariable=time_var, font=("Segoe UI", 18, "bold")).pack()

    running = [False]
    elapsed = [0]

    def update_timer():
        if running[0]:
            elapsed[0] += 1
            h, m, s = elapsed[0] // 3600, (elapsed[0] % 3600) // 60, elapsed[0] % 60
            time_var.set(f"{h:02d}:{m:02d}:{s:02d}")
            frame.after(1000, update_timer)

    def start_pause():
        running[0] = not running[0]
        if running[0]:
            update_timer()

    def reset_timer():
        running[0] = False
        elapsed[0] = 0
        time_var.set("00:00:00")

    ttk.Button(timer_frame, text="⏯ Start/Pause", bootstyle="primary", command=start_pause).pack(side="left", padx=5)
    ttk.Button(timer_frame, text="🔁 Reset", bootstyle="secondary", command=reset_timer).pack(side="left", padx=5)


def open_add_task_modal(username, parent_frame):
    modal = ttk.Toplevel()
    modal.title("Add New Task")
    modal.geometry("350x250")
    ttk.Label(modal, text="Task Title:").pack(anchor="w", padx=10, pady=(10, 0))
    title_entry = ttk.Entry(modal)
    title_entry.pack(fill="x", padx=10)

    ttk.Label(modal, text="Start Date (YYYY-MM-DD):").pack(anchor="w", padx=10, pady=(10, 0))
    start_entry = ttk.Entry(modal)
    start_entry.pack(fill="x", padx=10)

    ttk.Label(modal, text="Due Date (YYYY-MM-DD):").pack(anchor="w", padx=10, pady=(10, 0))
    due_entry = ttk.Entry(modal)
    due_entry.pack(fill="x", padx=10)

    def save_task():
        title = title_entry.get()
        start = start_entry.get()
        due = due_entry.get()
        if not title or not start or not due:
            Messagebox.show_error("Please fill all fields.")
            return
        try:
            datetime.strptime(start, "%Y-%m-%d")
            datetime.strptime(due, "%Y-%m-%d")
        except ValueError:
            Messagebox.show_error("Invalid date format. Use YYYY-MM-DD.")
            return
        db.add_task(username, title, start, due)
        Messagebox.show_info("Task added successfully!")
        modal.destroy()
        show_tasks(username, parent_frame)

    ttk.Button(modal, text="Save Task", bootstyle="success", command=save_task).pack(pady=20)


def show_analytic(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Analytics", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, text="Visual analytics coming soon.", font=("Segoe UI", 10)).pack(anchor="w")


def show_settings(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Settings", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, text="Customize your experience here.", font=("Segoe UI", 10)).pack(anchor="w")


def logout_action(root):
    if auth.logout():
        Messagebox.show_info("Logged out successfully.")
        for w in root.winfo_children():
            w.destroy()
        from login import LoginWindow
        LoginWindow(root)
    else:
        Messagebox.show_error("Logout failed.")
