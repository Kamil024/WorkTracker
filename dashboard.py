import tkinter as tk
from tkinter import ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

import db
import auth
import tasks
import analytics

# ---------- GLOBAL TIMER STATE ----------
TIMER_STATE = {
    "running": False,
    "seconds": 0.0,
    "label": None,
    "after_id": None,
    "root": None,
    "start_time": None,
    "base_seconds": 0.0,
}

# ---------- Dashboard ----------
def open_dashboard(user, root):
    username = user["username"]
    user_id = user["id"]

    for w in root.winfo_children():
        w.destroy()

    root.title(f"WorkTracker Pro — {username}")
    root.geometry("1280x780")
    root.minsize(1000, 600)
    root.unbind("<Return>")

    TIMER_STATE["root"] = root

    container = ttk.Frame(root)
    container.pack(fill="both", expand=True)
    container.columnconfigure(1, weight=1)
    container.rowconfigure(1, weight=1)

    # --- Topbar ---
    topbar = ttk.Frame(container, padding=(18, 10))
    topbar.grid(row=0, column=0, columnspan=2, sticky="ew")
    ttk.Label(topbar, text="WorkTracker Pro", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")

    right_area = ttk.Frame(topbar)
    right_area.grid(row=0, column=1, sticky="e")
    ttk.Button(right_area, text="🚪 Logout", command=lambda: logout_action(root)).pack(side="left", padx=8)
    ttk.Label(right_area, text=username[0].upper(), width=3, anchor="center",
              font=("Segoe UI", 11, "bold")).pack(side="left", padx=(6, 0))

    # --- Layout ---
    layout = ttk.Frame(container)
    layout.grid(row=1, column=0, columnspan=2, sticky="nsew")
    layout.columnconfigure(1, weight=1)
    layout.rowconfigure(0, weight=1)

    # --- Sidebar ---
    sidebar_width = tk.IntVar(value=220)
    sidebar = ttk.Frame(layout, padding=(12, 18))
    sidebar.grid(row=0, column=0, sticky="nsw")
    sidebar.config(width=sidebar_width.get())
    sidebar.pack_propagate(False)

    def nav_btn(icon, text, cmd):
        btn = ttk.Button(sidebar, command=cmd)
        btn.pack(fill="x", pady=6, ipady=6)
        frame = ttk.Frame(btn)
        frame.pack(fill="x")
        ttk.Label(frame, text=icon, font=("Segoe UI", 11)).pack(side="left", padx=(8, 0))
        btn.text_label = ttk.Label(frame, text=text, font=("Segoe UI", 10))
        btn.text_label.pack(side="left", padx=(10, 0))
        return btn

    # --- Navigation Buttons ---
    content = ttk.Frame(layout, padding=20)
    content.grid(row=0, column=1, sticky="nsew")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(2, weight=1)

    nav_btn("🏠", "Overview", lambda: show_welcome(user_id, username, content))
    nav_btn("📝", "Tasks", lambda: show_tasks(user_id, username, content))
    nav_btn("📊", "Analytics", lambda: show_analytic(username, content))
    nav_btn("⚙️", "Settings", lambda: show_settings(username, content))

    # --- Timer ---
    timer_frame = ttk.Frame(sidebar, padding=(10, 15))
    timer_frame.pack(side="bottom", fill="x", pady=(20, 10))
    ttk.Label(timer_frame, text="⏱ Focus Timer", font=("Segoe UI", 11, "bold")).pack()
    timer_label = ttk.Label(timer_frame, text="00:00:00", font=("Consolas", 18, "bold"))
    timer_label.pack(pady=5)

    TIMER_STATE["label"] = timer_label
    refresh_timer_label()

    btns = ttk.Frame(timer_frame)
    btns.pack(pady=5)
    ttk.Button(btns, text="▶", width=3, command=start_timer, bootstyle="success-outline").pack(side="left", padx=2)
    ttk.Button(btns, text="⏸", width=3, command=pause_timer, bootstyle="warning-outline").pack(side="left", padx=2)
    ttk.Button(btns, text="🔁", width=3, command=reset_timer, bootstyle="secondary-outline").pack(side="left", padx=2)

    show_welcome(user_id, username, content)

# ---------- Helper Functions ----------
def clear_frame(f):
    for w in f.winfo_children():
        w.destroy()

def card(parent, title, value, icon=None):
    f = ttk.Frame(parent, padding=12)
    f.pack(side="left", expand=True, fill="both", padx=8)
    ttk.Label(f, text=title, font=("Segoe UI", 9)).pack(anchor="w")
    ttk.Label(f, text=value, font=("Segoe UI", 18, "bold")).pack(anchor="center", pady=(8, 0))
    if icon:
        ttk.Label(f, text=icon, font=("Segoe UI Emoji", 16)).pack(anchor="e")

# ---------- Overview ----------
def show_welcome(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text=f"Welcome back, {username}!", font=("Segoe UI", 20, "bold")).pack(anchor="w")
    ttk.Label(frame, text="Your productivity overview for today.", font=("Segoe UI", 10),
              foreground="#6c757d").pack(anchor="w", pady=(4, 10))

    tasks_rows = tasks.get_tasks_rows(username)
    completed = in_progress = overdue = 0

    if tasks_rows:
        for t in tasks_rows:
            status = str(t[3]).strip().lower() if len(t) > 3 else ""
            if status == "completed":
                completed += 1
            elif status == "in progress":
                in_progress += 1
            elif status == "overdue":
                overdue += 1

    focus_time = completed * 60

    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill="x", pady=(18, 12))
    card(stats_frame, "Completed", completed, icon="✅")
    card(stats_frame, "In Progress", in_progress, icon="🔁")
    card(stats_frame, "Overdue", overdue, icon="⚠️")
    card(stats_frame, "Focus Time", f"{focus_time}m", icon="⏱")

    ttk.Label(frame, text="Recent Tasks", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(16, 6))
    if not tasks_rows:
        ttk.Label(frame, text="No recent tasks. Start one now!", foreground="#888").pack(anchor="w")
    else:
        for t in tasks_rows[:5]:
            title = t[0]
            due = t[2] if len(t) > 2 else "N/A"
            ttk.Label(frame, text=f"• {title} (Due: {due})", font=("Segoe UI", 10)).pack(anchor="w")

# ---------- Tasks ----------
def show_tasks(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Tasks", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    ttk.Button(frame, text="➕ Add Task",
               command=lambda: open_add_task_modal(user_id, username, frame)).pack(anchor="e", pady=(0, 8))

    rows = tasks.get_tasks_rows(username)
    columns = ["Title", "Start Date", "Due Date", "Status", "Priority", "Category"]
    normalized_rows = []
    for r in rows:
        title = r[0] if len(r) > 0 else ""
        start = r[1] if len(r) > 1 else ""
        due = r[2] if len(r) > 2 else ""
        status = r[3] if len(r) > 3 else ""
        priority = ""
        category = ""
        try:
            full = tasks.get_tasks_full_rows(username)
            for fr in full:
                if len(fr) >= 11 and fr[3] == title and str(fr[4]) == str(start):
                    priority = fr[8] or ""
                    category = fr[9] or ""
                    break
        except Exception:
            pass
        normalized_rows.append((title, start, due, status, priority, category))

    table = Tableview(master=frame, coldata=columns, rowdata=normalized_rows, paginated=False, searchable=True)
    table.pack(fill="both", expand=True, pady=(5, 0))

# ---------- Timer Logic ----------
def refresh_timer_label():
    if TIMER_STATE["label"]:
        sec = int(TIMER_STATE["seconds"])
        h = sec // 3600
        m = (sec % 3600) // 60
        s = sec % 60
        TIMER_STATE["label"].config(text=f"{h:02}:{m:02}:{s:02}")

def update_timer():
    if TIMER_STATE["running"]:
        current_time = time.time()
        elapsed = current_time - TIMER_STATE.get("start_time", current_time)
        TIMER_STATE["seconds"] = TIMER_STATE.get("base_seconds", 0) + elapsed
        refresh_timer_label()
    if TIMER_STATE.get("root"):
        TIMER_STATE["after_id"] = TIMER_STATE["root"].after(1000, update_timer)

def start_timer():
    if not TIMER_STATE["running"]:
        TIMER_STATE["running"] = True
        TIMER_STATE["start_time"] = time.time()
        TIMER_STATE["base_seconds"] = TIMER_STATE.get("seconds", 0)
        if not TIMER_STATE.get("after_id"):
            TIMER_STATE["after_id"] = TIMER_STATE["root"].after(1000, update_timer)

def pause_timer():
    if TIMER_STATE["running"]:
        TIMER_STATE["running"] = False
        TIMER_STATE["base_seconds"] = TIMER_STATE.get("seconds", 0)
        TIMER_STATE["start_time"] = None
    if TIMER_STATE.get("after_id") and TIMER_STATE.get("root"):
        try:
            TIMER_STATE["root"].after_cancel(TIMER_STATE["after_id"])
        except Exception:
            pass
        TIMER_STATE["after_id"] = None

def reset_timer():
    if TIMER_STATE.get("after_id") and TIMER_STATE.get("root"):
        try:
            TIMER_STATE["root"].after_cancel(TIMER_STATE["after_id"])
        except Exception:
            pass
        TIMER_STATE["after_id"] = None

    TIMER_STATE["running"] = False
    TIMER_STATE["seconds"] = 0
    TIMER_STATE["base_seconds"] = 0
    TIMER_STATE["start_time"] = None
    refresh_timer_label()

# ---------- Add Task Modal ----------
def open_add_task_modal(user_id, username, parent_frame):
    modal = tk.Toplevel()
    modal.title("Add New Task")
    modal.geometry("480x520")
    modal.resizable(False, False)
    modal.transient(TIMER_STATE.get("root"))
    modal.grab_set()

    padding = {"padx": 12, "pady": 6}

    ttk.Label(modal, text="Add New Task", font=("Segoe UI", 14, "bold")).pack(anchor="center", pady=(10, 4))
    ttk.Label(modal, text="Create a new task to track your progress.", font=("Segoe UI", 9),
              foreground="#6c757d").pack(anchor="center", pady=(0, 8))

    ttk.Label(modal, text="Title", font=("Segoe UI", 10)).pack(anchor="w", **padding)
    title_entry = ttk.Entry(modal)
    title_entry.pack(fill="x", **padding)

    ttk.Label(modal, text="Description (optional)", font=("Segoe UI", 10)).pack(anchor="w", **padding)
    desc_text = tk.Text(modal, height=4, wrap="word")
    desc_text.pack(fill="x", **padding)

    row1 = ttk.Frame(modal)
    row1.pack(fill="x", **padding)
    row1.columnconfigure((0, 1), weight=1)
    ttk.Label(row1, text="Priority", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
    ttk.Label(row1, text="Category", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w")

    priority_combo = ttk.Combobox(row1, values=["Low", "Medium", "High"], state="readonly")
    priority_combo.set("Medium")
    priority_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 0))

    category_combo = ttk.Combobox(row1, values=["Work", "Personal", "Study", "Other"], state="readonly")
    category_combo.grid(row=1, column=1, sticky="ew", pady=(4, 0))

    row2 = ttk.Frame(modal)
    row2.pack(fill="x", **padding)
    row2.columnconfigure((0, 1), weight=1)
    ttk.Label(row2, text="Deadline (optional)", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w")
    ttk.Label(row2, text="Estimated Time (minutes)", font=("Segoe UI", 9)).grid(row=0, column=1, sticky="w")

    deadline_entry = DateEntry(row2, dateformat="%Y-%m-%d", startdate=datetime.now())
    deadline_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 0))

    est_entry = ttk.Entry(row2)
    est_entry.insert(0, "60")
    est_entry.grid(row=1, column=1, sticky="ew", pady=(4, 0))

    btn_frame = ttk.Frame(modal)
    btn_frame.pack(fill="x", pady=(10, 12), padx=12)

    def _cancel():
        modal.grab_release()
        modal.destroy()

    def _save():
        title = title_entry.get().strip()
        description = desc_text.get("1.0", "end").strip() or None
        priority = priority_combo.get().strip() or "Medium"
        category = category_combo.get().strip() or "Work"
        due = deadline_entry.entry.get().strip() or None
        est_text = est_entry.get().strip()
        try:
            est_minutes = int(est_text) if est_text else 0
        except ValueError:
            Messagebox.show_error("Estimated time must be a number (minutes).")
            return
        if not title:
            Messagebox.show_error("Please enter a task title.")
            return

        confirm = Messagebox.yesno("Create Task", f"Are you sure you want to create the task '{title}'?")
        if confirm != "Yes":
            return

        success = tasks.add_new_task(
            user_id, username, title, datetime.now().strftime("%Y-%m-%d"), due, "In Progress",
            description=description, priority=priority, category=category, estimated_minutes=est_minutes
        )
        if success:
            Messagebox.show_info("Task added successfully!")
            modal.grab_release()
            modal.destroy()
            show_tasks(user_id, username, parent_frame)
        else:
            Messagebox.show_error("Failed to add task. Please try again.")

    ttk.Button(btn_frame, text="Cancel", command=_cancel, bootstyle="secondary").pack(side="left", expand=True, padx=5)
    ttk.Button(btn_frame, text="Create Task", command=_save, bootstyle="primary").pack(side="right", expand=True, padx=5)

    title_entry.focus_set()

# ---------- Analytics ----------
def show_analytic(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Analytics", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))
    ttk.Label(frame, text=f"Comprehensive productivity insights for {username}.",
              font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w", pady=(0, 15))

    full_rows = tasks.get_tasks_full_rows(username)
    if not full_rows:
        ttk.Label(frame, text="No tasks found to analyze.", foreground="#888").pack(anchor="w", pady=10)
        return

    df = analytics.build_tasks_dataframe(full_rows)
    stats = analytics.compute_stats(df)

    stats_frame = ttk.Frame(frame)
    stats_frame.pack(fill="x", pady=8)
    card(stats_frame, "Total Tasks", stats["total"], "📋")
    card(stats_frame, "Completed", stats["completed"], "✅")
    card(stats_frame, "In Progress", stats["in_progress"], "🔁")
    card(stats_frame, "Overdue", stats["overdue"], "⚠️")

    monthly_counts = stats["monthly_counts"]

    fig = Figure(figsize=(10, 4), dpi=100)
    ax1 = fig.add_subplot(131)
    ax2 = fig.add_subplot(132)
    ax3 = fig.add_subplot(133)

    if not monthly_counts.empty:
        ax1.bar(monthly_counts.index.astype(str), monthly_counts.values)
    else:
        ax1.text(0.5, 0.5, "No data", ha="center", va="center", color="#888")
    ax1.set_title("Tasks per Month", fontsize=9)
    ax1.tick_params(axis="x", rotation=45)

    labels = ["Completed", "In Progress", "Overdue"]
    values = [stats["completed"], stats["in_progress"], stats["overdue"]]
    ax2.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Task Distribution", fontsize=9)

    if "Due" in df.columns and not df["Due"].isna().all():
        df_sorted = df.sort_values("Due")
        ax3.plot(df_sorted["Due"], range(1, len(df_sorted) + 1), marker="o")
        ax3.set_title("Task Timeline", fontsize=9)
        ax3.tick_params(axis="x", rotation=30)
    else:
        ax3.text(0.5, 0.5, "No due date data", ha="center", va="center", color="#888")

    chart_frame = ttk.Frame(frame)
    chart_frame.pack(fill="both", expand=True, pady=(10, 20))
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

# ---------- Settings ----------
def show_settings(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Settings", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, text="Customize your experience here.", font=("Segoe UI", 10)).pack(anchor="w")

# ---------- Logout ----------
def logout_action(root):
    if TIMER_STATE.get("after_id") and TIMER_STATE.get("root"):
        try:
            TIMER_STATE["root"].after_cancel(TIMER_STATE["after_id"])
        except Exception:
            pass
        TIMER_STATE["after_id"] = None

    if auth.logout():
        Messagebox.show_info("Logged out successfully.")
        root.destroy()
    else:
        Messagebox.show_error("Logout failed.")
