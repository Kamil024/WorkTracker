import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
import tkinter as tk
import db
import auth

def open_dashboard(user, root):
    username = user["username"] if isinstance(user, dict) and "username" in user else str(user)

    for w in root.winfo_children():
        w.destroy()

    root.title(f"WorkTracker Pro — {username}")
    root.geometry("1280x780")
    root.minsize(1000, 600)

    style = ttk.Style("litera")

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)

    container.columnconfigure(0, weight=0)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(1, weight=1)

    # Top bar
    topbar = ttk.Frame(container, padding=(18, 10), bootstyle="light")
    topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
    topbar.columnconfigure(0, weight=1)

    # Left brand (only WorkTracker Pro)
    left_brand = ttk.Frame(topbar)
    left_brand.grid(row=0, column=0, sticky="w")
    ttk.Label(left_brand, text="WorkTracker Pro", font=("Segoe UI", 14, "bold")).pack(side="left")

    # Right area (Logout and user icon)
    right_area = ttk.Frame(topbar)
    right_area.grid(row=0, column=1, sticky="e")

    ttk.Button(
        right_area, 
        text="🚪 Logout", 
        bootstyle="danger", 
        command=lambda: logout_action(root)
    ).pack(side="left", padx=8)

    ttk.Label(right_area, text="  ").pack(side="left", padx=4)
    ttk.Label(
        right_area, 
        text=username[0].upper(), 
        bootstyle="primary-inverse", 
        width=3, 
        anchor="center"
    ).pack(side="left", padx=(6,0))

    # Main layout
    layout = ttk.Frame(container)
    layout.grid(row=1, column=0, columnspan=2, sticky="nsew")
    layout.columnconfigure(0, weight=0)
    layout.columnconfigure(1, weight=1)
    layout.rowconfigure(0, weight=1)

    # Sidebar
    sidebar = ttk.Frame(layout, padding=(12, 18), bootstyle="light")
    sidebar.grid(row=0, column=0, sticky="nsw")
    sidebar.config(width=220)
    sidebar.pack_propagate(False)

    brand = ttk.Label(sidebar, text="WorkTracker Pro", font=("Segoe UI", 12, "bold"))
    brand.pack(anchor="w", pady=(0, 16))

    def nav_btn(text, cmd, active=False):
        bs = "dark" if active else "light"
        b = ttk.Button(sidebar, text=text, bootstyle=f"{bs}-outline", command=cmd)
        b.pack(fill="x", pady=6, ipady=6)
        return b

    nav_btn("Overview", lambda: show_welcome(username, content), active=True)
    nav_btn("Tasks", lambda: show_tasks(username, content))
    nav_btn("Timer", lambda: show_timer(username, content))
    nav_btn("Analytics", lambda: show_analytic(username, content))
    nav_btn("Settings", lambda: show_settings(username, content))

    # Content area
    content = ttk.Frame(layout, padding=20)
    content.grid(row=0, column=1, sticky="nsew")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(2, weight=1)

    show_welcome(username, content)

def clear_frame(f):
    for w in f.winfo_children():
        w.destroy()

def card(parent, title, value, icon=None):
    f = ttk.Frame(parent, padding=12, bootstyle="light")
    f.pack(side="left", expand=True, fill="both", padx=8)
    ttk.Label(f, text=title, font=("Segoe UI", 9)).pack(anchor="w")
    ttk.Label(f, text=value, font=("Segoe UI", 18, "bold")).pack(anchor="center", pady=(8,0))
    if icon:
        ttk.Label(f, text=icon, font=("Segoe UI Emoji", 16)).pack(anchor="e")

def show_welcome(username, frame):
    clear_frame(frame)
    header_frame = ttk.Frame(frame)
    header_frame.pack(fill="x", pady=(0,12))
    ttk.Label(header_frame, text=f"Welcome back, {username}!", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(header_frame, text="Here's your productivity overview for today.", font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w", pady=(6,0))

    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill="x", pady=(18,12))
    card(stats_frame, "Completed Today", "0", icon="✅")
    card(stats_frame, "In Progress", "0", icon="🔁")
    card(stats_frame, "Overdue", "0", icon="⚠️")
    card(stats_frame, "Time Today", "0m", icon="⏱")

    bottom = ttk.Frame(frame)
    bottom.pack(fill="both", expand=True, pady=(12,0))
    left = ttk.Frame(bottom)
    left.pack(side="left", fill="both", expand=True, padx=(0,12))
    right = ttk.Frame(bottom)
    right.pack(side="left", fill="both", expand=True)

    recent = ttk.Frame(left, padding=12, bootstyle="light")
    recent.pack(fill="both", expand=True)
    ttk.Label(recent, text="Recent Tasks", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    ttk.Label(recent, text="Your latest task activity", font=("Segoe UI", 9), foreground="#6c757d").pack(anchor="w", pady=(2,10))
    body = ttk.Frame(recent)
    body.pack(fill="both", expand=True)
    ttk.Label(body, text="No tasks yet. Create your first task!", font=("Segoe UI", 10), foreground="#7a7a7a").pack(expand=True)

    timer_card = ttk.Frame(right, padding=12, bootstyle="light")
    timer_card.pack(fill="both", expand=True)
    ttk.Label(timer_card, text="Quick Timer", font=("Segoe UI", 11, "bold")).pack(anchor="w")
    ttk.Label(timer_card, text="Start a focused work session", font=("Segoe UI", 9), foreground="#6c757d").pack(anchor="w", pady=(2,10))
    circle = ttk.Frame(timer_card, width=110, height=110, bootstyle="light")
    circle.pack(pady=20)
    circle.pack_propagate(False)
    ttk.Label(circle, text="◯", font=("Segoe UI", 32), foreground="#bdbdbd").pack(expand=True)
    ttk.Label(timer_card, text="Ready to Work", font=("Segoe UI", 10, "bold")).pack()
    ttk.Button(timer_card, text="Start", bootstyle="dark").pack(pady=(10,0))

def show_tasks(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Tasks", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,12))
    rows = db.get_tasks(username)
    columns = ["Title", "Start Date", "Due Date"]
    table = Tableview(master=frame, coldata=columns, rowdata=rows, paginated=False, searchable=True)
    table.pack(fill="both", expand=True)

def show_timer(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Timer", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,12))
    ttk.Label(frame, text="Timer coming soon.", font=("Segoe UI", 10)).pack(anchor="w")

def show_analytic(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Analytics", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,12))
    ttk.Label(frame, text="Analytics coming soon.", font=("Segoe UI", 10)).pack(anchor="w")

def show_settings(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Settings", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0,12))
    ttk.Label(frame, text="Settings coming soon.", font=("Segoe UI", 10)).pack(anchor="w")

def logout_action(root):
    if auth.logout():
        Messagebox.show_info("Logged out successfully.")
        for w in root.winfo_children():
            w.destroy()
        from login import LoginWindow
        LoginWindow(root)
    else:
        Messagebox.show_error("Logout failed.")
