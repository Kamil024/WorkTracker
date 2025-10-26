import tkinter as tk
from tkinter import ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

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
    root.geometry("1600x820")
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
    sidebar = ttk.Frame(layout, padding=(12, 18))
    sidebar.grid(row=0, column=0, sticky="nsw")
    sidebar.config(width=220)
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

    # --- Content ---
    content = ttk.Frame(layout, padding=20)
    content.grid(row=0, column=1, sticky="nsew")
    content.columnconfigure(0, weight=1)
    content.rowconfigure(2, weight=1)

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


# ---------- Add Task Modal ----------
def open_add_task_modal(user_id, username, parent_frame):
    modal = tk.Toplevel()
    modal.title("Add New Task")
    modal.geometry("360x330")
    modal.resizable(False, False)

    ttk.Label(modal, text="Task Title:").pack(anchor="w", padx=10, pady=(10, 0))
    title_entry = ttk.Entry(modal)
    title_entry.pack(fill="x", padx=10)

    ttk.Label(modal, text="Start Date:").pack(anchor="w", padx=10, pady=(10, 0))
    start_picker = DateEntry(modal, dateformat="%Y-%m-%d", startdate=datetime.now(), width=20)
    start_picker.pack(fill="x", padx=10)

    ttk.Label(modal, text="Due Date:").pack(anchor="w", padx=10, pady=(10, 0))
    due_picker = DateEntry(modal, dateformat="%Y-%m-%d", startdate=datetime.now(), width=20)
    due_picker.pack(fill="x", padx=10)

    ttk.Label(modal, text="Status:").pack(anchor="w", padx=10, pady=(10, 0))
    status_combo = ttk.Combobox(modal, values=["In Progress", "Completed", "Overdue"], state="readonly")
    status_combo.set("In Progress")
    status_combo.pack(fill="x", padx=10)

    def save_task():
        title = title_entry.get().strip()
        start = start_picker.entry.get()
        due = due_picker.entry.get()
        status = status_combo.get()

        if not title:
            Messagebox.show_error("Please enter a task title.")
            return

        success = tasks.add_new_task(user_id, username, title, start, due, status)
        if success:
            Messagebox.show_info("Task added successfully!")
            modal.destroy()
            show_tasks(user_id, username, parent_frame)
        else:
            Messagebox.show_error("Failed to add task. Please try again.")

    ttk.Button(modal, text="Save Task", command=save_task).pack(pady=20)


# ---------- Edit Task Modal ----------
def open_edit_task_modal(user_id, username, parent_frame):
    table = getattr(parent_frame, "table", None)
    if not table:
        Messagebox.show_error("No table found.")
        return

    selected = table.view.selection()
    if not selected:
        Messagebox.show_error("Please select a task to edit.")
        return

    selected_item = table.view.item(selected[0])["values"]
    if not selected_item or len(selected_item) < 4:
        Messagebox.show_error("Invalid task data.")
        return

    title_old, start_old, due_old, status_old = selected_item

    modal = tk.Toplevel()
    modal.title("Edit Task")
    modal.geometry("360x330")
    modal.resizable(False, False)

    ttk.Label(modal, text="Task Title:").pack(anchor="w", padx=10, pady=(10, 0))
    title_entry = ttk.Entry(modal)
    title_entry.insert(0, title_old)
    title_entry.pack(fill="x", padx=10)

    ttk.Label(modal, text="Start Date:").pack(anchor="w", padx=10, pady=(10, 0))
    start_picker = DateEntry(modal, dateformat="%Y-%m-%d", width=20)
    start_picker.entry.delete(0, "end")
    start_picker.entry.insert(0, start_old)
    start_picker.pack(fill="x", padx=10)

    ttk.Label(modal, text="Due Date:").pack(anchor="w", padx=10, pady=(10, 0))
    due_picker = DateEntry(modal, dateformat="%Y-%m-%d", width=20)
    due_picker.entry.delete(0, "end")
    due_picker.entry.insert(0, due_old)
    due_picker.pack(fill="x", padx=10)

    ttk.Label(modal, text="Status:").pack(anchor="w", padx=10, pady=(10, 0))
    status_combo = ttk.Combobox(modal, values=["In Progress", "Completed", "Overdue"], state="readonly")
    status_combo.set(status_old)
    status_combo.pack(fill="x", padx=10)

    def save_changes():
        new_title = title_entry.get().strip()
        new_start = start_picker.entry.get()
        new_due = due_picker.entry.get()
        new_status = status_combo.get()

        if not new_title:
            Messagebox.show_error("Please enter a task title.")
            return

        success = tasks.update_task(user_id, username, title_old, new_title, new_start, new_due, new_status)
        if success:
            Messagebox.show_info("Task updated successfully!")
            modal.destroy()
            show_tasks(user_id, username, parent_frame)
        else:
            Messagebox.show_error("Failed to update task.")

    ttk.Button(modal, text="💾 Save Changes", command=save_changes).pack(pady=20)


# ---------- Tasks Page ----------
def show_tasks(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Tasks", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=(0, 8))
    ttk.Button(btn_frame, text="➕ Add Task",
               command=lambda: open_add_task_modal(user_id, username, frame)).pack(side="right", padx=(4, 0))
    ttk.Button(btn_frame, text="✏️ Edit Task",
               command=lambda: open_edit_task_modal(user_id, username, frame)).pack(side="right", padx=(0, 4))

    rows = tasks.get_tasks_rows(username)
    columns = ["Title", "Start Date", "Due Date", "Status"]
    table = Tableview(master=frame, coldata=columns, rowdata=rows, paginated=False, searchable=True)
    table.pack(fill="both", expand=True, pady=(5, 0))
    frame.table = table


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


# ---------- Analytics ----------
def show_analytic(username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Analytics", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))
    ttk.Label(frame, text=f"Comprehensive productivity insights for {username}.",
              font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w", pady=(0, 15))

    rows = tasks.get_tasks_rows(username)
    if not rows:
        ttk.Label(frame, text="No tasks found to analyze.", foreground="#888").pack(anchor="w", pady=10)
        return

    df = analytics.build_tasks_dataframe(rows)
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

    ax1.bar(monthly_counts.index.astype(str), monthly_counts.values)
    ax1.set_title("Tasks per Month", fontsize=9)
    ax1.tick_params(axis="x", rotation=45)

    labels = ["Completed", "In Progress", "Overdue"]
    values = [stats["completed"], stats["in_progress"], stats["overdue"]]
    ax2.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax2.set_title("Task Distribution", fontsize=9)

    if not df["Due"].isna().all():
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
    # Stop timer if running
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

    # Confirm logout
    confirm = Messagebox.okcancel("Are you sure you want to logout?", "Logout Confirmation")
    if not confirm:
        return

    # Perform logout process
    if auth.logout():
        Messagebox.show_info("You have been logged out successfully.", "Logout")

        # Clear dashboard UI
        for widget in root.winfo_children():
            widget.destroy()

        # Reset window size and title for login
        root.geometry("1000x600")  # 👈 Restore to original login window size
        root.minsize(400, 400)
        root.title("Work Tracker — Login")

        # Reopen login window
        import login
        login.open_login_window(root)
    else:
        Messagebox.show_error("Logout failed. Please try again.", "Error")


