import tkinter as tk
from tkinter import ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os

# Pillow for image handling
from PIL import Image, ImageTk, ImageOps

import db
import auth
import tasks
import analytics

#  DYNAMIC AVATAR PATH 
AVATAR_DIR = os.path.join(os.path.dirname(__file__), "avatars")

#  GLOBAL TIMER STATE 
TIMER_STATE = {
    "running": False,
    "seconds": 0.0,
    "label": None,
    "after_id": None,
    "root": None,
    "start_time": None,
    "base_seconds": 0.0,
}

# Avatar unlock mapping (filename -> required level)
AVATAR_UNLOCKS = [
    ("female_1.png", 1),
    ("female_2.png", 4),
    ("female_3.png", 7),
    ("female_4.png", 10),
    ("female_5.png", 13),
    ("male_1.png", 16),
    ("male_2.png", 19),
    ("male_3.png", 23),
    ("male_4.png", 27),
]


#  Dashboard 
def open_dashboard(user, root):
    username = user["username"]
    user_id = user["id"]

    for w in root.winfo_children():
        w.destroy()

    root.title(f"WorkTracker — {username}")
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
    ttk.Label(topbar, text="WorkTracker", font=("Segoe UI", 14, "bold")).grid(row=0, column=0, sticky="w")

    right_area = ttk.Frame(topbar)
    right_area.grid(row=0, column=1, sticky="e")

    # get equipped avatar (small)
    reward = db.get_reward_data(user_id)
    avatar_filename = reward.get("avatar", "female_1.png")
    avatar_img_small = _load_avatar_thumbnail(avatar_filename, size=(28, 28))

    if avatar_img_small:
        avatar_lbl = ttk.Label(right_area, image=avatar_img_small)
        avatar_lbl.image = avatar_img_small
        avatar_lbl.pack(side="left", padx=(0, 6))

    ttk.Button(right_area, text="🚪 Logout", command=lambda: logout_action(root)).pack(side="left", padx=8)
    ttk.Label(right_area, text=username[0].upper(), width=3, anchor="center",
              font=("Segoe UI", 11, "bold")).pack(side="left", padx=(6, 0))

    #  Layout 
    layout = ttk.Frame(container)
    layout.grid(row=1, column=0, columnspan=2, sticky="nsew")
    layout.columnconfigure(1, weight=1)
    layout.rowconfigure(0, weight=1)

    #  Sidebar 
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

    #  Navigation Buttons 
    nav_btn("🏠", "Overview", lambda: show_welcome(user_id, username, content))
    nav_btn("📝", "Tasks", lambda: show_tasks(user_id, username, content))
    nav_btn("📊", "Analytics", lambda: show_analytic(username, content))
    nav_btn("🏆", "Rewards", lambda: show_rewards(user_id, username, content))
    nav_btn("⚙️", "Settings", lambda: show_settings(user_id, username, content))

    # Admin tab only for admin user
    if username == "admin":
        nav_btn("🛠", "Admin Panel", lambda: show_admin_panel(user_id, username, content))

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


#  Helper Functions 
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

def _load_avatar_thumbnail(filename, size=(64,64), greyscale=False):
    """
    Load avatar image from AVATAR_DIR and return a PhotoImage.
    If image missing, returns None.
    """
    try:
        path = os.path.join(AVATAR_DIR, filename)
        if not os.path.exists(path):
            return None
        img = Image.open(path).convert("RGBA")
        img = img.resize(size, Image.LANCZOS)
        if greyscale:
            img = ImageOps.grayscale(img).convert("RGBA")
        return ImageTk.PhotoImage(img)
    except Exception:
        return None

#  Add Task Modal (modern, compatible) 
def open_add_task_modal(user_id, username, parent_frame):
    modal = tk.Toplevel()
    modal.title("Add New Task")
    modal.geometry("420x520")
    modal.resizable(False, False)

    # Header
    header_frame = ttk.Frame(modal, padding=(14, 8))
    header_frame.pack(fill="x")
    ttk.Label(header_frame, text="Add New Task", font=("Segoe UI Semibold", 14)).pack(anchor="w")
    ttk.Label(header_frame, text="Create a new task to track your progress.", font=("Segoe UI", 9), foreground="#6B728E").pack(anchor="w", pady=(2, 6))

    form = ttk.Frame(modal, padding=(14, 8))
    form.pack(fill="both", expand=True)

    # Title
    ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w", pady=(6, 2))
    title_entry = ttk.Entry(form)
    title_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    form.columnconfigure(0, weight=1)

    # Description
    ttk.Label(form, text="Description (optional)").grid(row=2, column=0, sticky="w", pady=(6, 2))
    description_text = tk.Text(form, height=5, wrap="word")
    description_text.grid(row=3, column=0, sticky="ew", pady=(0, 8))

    # Row: Priority & Category side-by-side
    left_right = ttk.Frame(form)
    left_right.grid(row=4, column=0, sticky="ew", pady=(6, 0))
    left_right.columnconfigure(0, weight=1)
    left_right.columnconfigure(1, weight=1)

    # Priority
    ttk.Label(left_right, text="Priority").grid(row=0, column=0, sticky="w")
    priority_combo = ttk.Combobox(left_right, values=["Low", "Medium", "High"], state="readonly")
    priority_combo.set("Medium")
    priority_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 8))

    # Category
    ttk.Label(left_right, text="Category").grid(row=0, column=1, sticky="w")
    category_combo = ttk.Combobox(left_right, values=["Work", "Study", "Personal", "Other"], state="readonly")
    category_combo.set("Work")
    category_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 8))

    # Row: Deadline & Estimated Time side-by-side
    lr2 = ttk.Frame(form)
    lr2.grid(row=5, column=0, sticky="ew", pady=(2, 0))
    lr2.columnconfigure(0, weight=1)
    lr2.columnconfigure(1, weight=1)

    # Deadline
    ttk.Label(lr2, text="Deadline (optional)").grid(row=0, column=0, sticky="w")
    deadline_picker = DateEntry(lr2, dateformat="%Y-%m-%d", startdate=datetime.now(), width=20)
    deadline_picker.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 8))

    # Estimated Time
    ttk.Label(lr2, text="Estimated Time (minutes)").grid(row=0, column=1, sticky="w")
    estimated_entry = ttk.Entry(lr2)
    estimated_entry.insert(0, "60")
    estimated_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 8))

    # Buttons
    btn_frame = ttk.Frame(modal, padding=(14, 8))
    btn_frame.pack(fill="x")
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    def cancel():
        modal.destroy()

    def create_task():
        title = title_entry.get().strip()
        description = description_text.get("1.0", "end").strip()
        priority = priority_combo.get()
        category = category_combo.get()
        deadline = deadline_picker.entry.get()
        estimated = estimated_entry.get().strip()

        if not title:
            Messagebox.show_error("Please enter a task title.")
            return

        try:
            estimated_minutes = int(estimated)
        except Exception:
            estimated_minutes = 0

        # Use tasks.add_new_task signature that accepts extended fields.
        success = tasks.add_new_task(
            user_id=user_id,
            username=username,
            title=title,
            start_date=datetime.now().strftime("%Y-%m-%d"),
            due_date=deadline,
            status="In Progress",
            description=description if description else None,
            priority=priority,
            category=category,
            estimated_minutes=estimated_minutes
        )

        if success:
            Messagebox.show_info("Task created successfully!")
            modal.destroy()
            show_tasks(user_id, username, parent_frame)
        else:
            Messagebox.show_error("Failed to create task. Please try again.")

    ttk.Button(btn_frame, text="Cancel", command=cancel, bootstyle="secondary-outline").grid(row=0, column=0, sticky="ew", padx=(0, 6))
    ttk.Button(btn_frame, text="Create Task", command=create_task, bootstyle="primary").grid(row=0, column=1, sticky="ew", padx=(6, 0))


#  Delete Task Function 
def delete_task_action(user_id, username, parent_frame):
    """Delete selected task with confirmation."""
    table = getattr(parent_frame, "table", None)
    if not table:
        Messagebox.show_error("No table found.")
        return

    selected = table.view.selection()
    if not selected:
        Messagebox.show_error("Please select a task to delete.")
        return

    selected_item = table.view.item(selected[0])["values"]
    if not selected_item:
        Messagebox.show_error("Invalid task data.")
        return

    # Support both old 4-column rows and new 6-column rows
    if len(selected_item) >= 6:
        title = selected_item[0]
        start_date = selected_item[3]
    elif len(selected_item) >= 4:
        title = selected_item[0]
        start_date = selected_item[1]
    else:
        Messagebox.show_error("Invalid task data format.")
        return

    # Confirm deletion
    confirm = Messagebox.okcancel(
        f"Are you sure you want to delete the task:\n\n'{title}'?\n\nThis action cannot be undone.",
        "Confirm Deletion"
    )
    
    if not confirm:
        return

    # Perform deletion
    success = tasks.safe_delete_task(username, title)
    
    if success:
        Messagebox.show_info("Task deleted successfully!")
        show_tasks(user_id, username, parent_frame)
    else:
        Messagebox.show_error("Failed to delete task. Please try again.")


#  Edit Task Modal (updated to handle extended fields when available) 
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
    if not selected_item:
        Messagebox.show_error("Invalid task data.")
        return

    # Support both old 4-column rows and new 6-column rows:
    # old: [title, start_date, due_date, status]
    # new: [title, category, est_minutes, start_date, due_date, status]
    if len(selected_item) >= 6:
        title_old = selected_item[0]
        category_old = selected_item[1]
        estimated_old = selected_item[2]
        start_old = selected_item[3]
        due_old = selected_item[4]
        status_old = selected_item[5]
    elif len(selected_item) >= 4:
        title_old, start_old, due_old, status_old = selected_item[:4]
        category_old = None
        estimated_old = None
    else:
        Messagebox.show_error("Invalid task data format.")
        return

    # Try to fetch the full row (if available) to get description/priority/category/estimated_minutes
    full_rows = tasks.get_tasks_full_rows(username)
    full_row = None
    for r in full_rows:
        try:
            # r = (id, user_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes)
            if r[3] == title_old and str(r[4]) == str(start_old):
                full_row = r
                break
        except Exception:
            continue
    if not full_row:
        for r in full_rows:
            try:
                if r[3] == title_old:
                    full_row = r
                    break
            except Exception:
                continue

    modal = tk.Toplevel()
    modal.title("Edit Task")
    modal.geometry("420x520")
    modal.resizable(False, False)

    header_frame = ttk.Frame(modal, padding=(14, 8))
    header_frame.pack(fill="x")
    ttk.Label(header_frame, text="Edit Task", font=("Segoe UI Semibold", 14)).pack(anchor="w")

    form = ttk.Frame(modal, padding=(14, 8))
    form.pack(fill="both", expand=True)

    # Title
    ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w", pady=(6, 2))
    title_entry = ttk.Entry(form)
    title_entry.insert(0, title_old)
    title_entry.grid(row=1, column=0, sticky="ew", pady=(0, 8))
    form.columnconfigure(0, weight=1)

    # Description
    ttk.Label(form, text="Description (optional)").grid(row=2, column=0, sticky="w", pady=(6, 2))
    description_text = tk.Text(form, height=5, wrap="word")
    description_text.grid(row=3, column=0, sticky="ew", pady=(0, 8))
    if full_row and len(full_row) >= 8 and full_row[7]:
        description_text.insert("1.0", str(full_row[7]))

    # Priority & Category
    lr = ttk.Frame(form)
    lr.grid(row=4, column=0, sticky="ew", pady=(6, 0))
    lr.columnconfigure(0, weight=1)
    lr.columnconfigure(1, weight=1)

    ttk.Label(lr, text="Priority").grid(row=0, column=0, sticky="w")
    priority_combo = ttk.Combobox(lr, values=["Low", "Medium", "High"], state="readonly")
    priority_combo.set("Medium")
    priority_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 8))

    ttk.Label(lr, text="Category").grid(row=0, column=1, sticky="w")
    category_combo = ttk.Combobox(lr, values=["Work", "Study", "Personal", "Other"], state="readonly")
    category_combo.set("Work")
    category_combo.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 8))

    if full_row and len(full_row) >= 10:
        try:
            if full_row[8]:
                priority_combo.set(full_row[8])
            if full_row[9]:
                category_combo.set(full_row[9])
        except Exception:
            pass
    else:
        # if we had category_old from table, seed it
        if category_old:
            try:
                category_combo.set(category_old)
            except Exception:
                pass

    # Deadline & Estimated Time
    lr2 = ttk.Frame(form)
    lr2.grid(row=5, column=0, sticky="ew", pady=(2, 0))
    lr2.columnconfigure(0, weight=1)
    lr2.columnconfigure(1, weight=1)

    ttk.Label(lr2, text="Deadline (optional)").grid(row=0, column=0, sticky="w")
    deadline_picker = DateEntry(lr2, dateformat="%Y-%m-%d", startdate=datetime.now(), width=20)
    deadline_picker.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(2, 8))
    if due_old:
        try:
            deadline_picker.entry.delete(0, "end")
            deadline_picker.entry.insert(0, due_old)
        except Exception:
            pass

    ttk.Label(lr2, text="Estimated Time (minutes)").grid(row=0, column=1, sticky="w")
    estimated_entry = ttk.Entry(lr2)
    estimated_entry.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(2, 8))
    if full_row and len(full_row) >= 11 and full_row[10] is not None:
        try:
            estimated_entry.insert(0, str(full_row[10]))
        except Exception:
            pass
    else:
        if estimated_old:
            try:
                estimated_entry.insert(0, str(estimated_old))
            except Exception:
                pass

    # Status
    ttk.Label(form, text="Status").grid(row=6, column=0, sticky="w", pady=(6, 2))
    status_combo = ttk.Combobox(form, values=["In Progress", "Completed", "Overdue"], state="readonly")
    status_combo.set(status_old)
    status_combo.grid(row=7, column=0, sticky="ew", pady=(0, 8))

    # Buttons
    btn_frame = ttk.Frame(modal, padding=(14, 8))
    btn_frame.pack(fill="x")
    btn_frame.columnconfigure(0, weight=1)
    btn_frame.columnconfigure(1, weight=1)

    def save_changes():
        new_title = title_entry.get().strip()
        new_description = description_text.get("1.0", "end").strip()
        new_priority = priority_combo.get()
        new_category = category_combo.get()
        new_due = deadline_picker.entry.get()
        new_estimated = estimated_entry.get().strip()
        new_status = status_combo.get()
        new_start = start_old  # keep original start unless changed explicitly

        if not new_title:
            Messagebox.show_error("Please enter a task title.")
            return

        try:
            estimated_minutes = int(new_estimated)
        except Exception:
            estimated_minutes = 0

        # Remember previous status to award EXP only when transitioning to Completed
        prev_status = status_old

        # Call tasks.update_task in the dashboard-style pattern:
        # (user_id, username, title_old, new_title, new_start, new_due, new_status, ...)
        try:
            success = tasks.update_task(
                user_id,
                username,
                title_old,
                new_title,
                new_start,
                new_due,
                new_status,
                description=new_description if new_description else None,
                priority=new_priority,
                category=new_category,
                estimated_minutes=estimated_minutes
            )
        except Exception:
            # fallback: call in positional signature that some older tasks.update_task might expect
            try:
                success = tasks.update_task(
                    title_old,  # not ideal but try anything
                    username,
                    new_title,
                    new_start,
                    new_due,
                    new_status
                )
            except Exception:
                success = False

        if success:
            # If newly marked completed and previously wasn't, award EXP
            if prev_status != "Completed" and new_status == "Completed":
                res = db.add_exp(user_id, 10)
                if res.get("success"):
                    if res.get("leveled_up"):
                        Messagebox.show_info(f"Task completed! +10 EXP — Level up! Now Level {res.get('level')}")
                    else:
                        Messagebox.show_info("Task completed! +10 EXP")
            else:
                Messagebox.show_info("Task updated successfully!")

            modal.destroy()
            show_tasks(user_id, username, parent_frame)
        else:
            Messagebox.show_error("Failed to update task.")

    ttk.Button(btn_frame, text="💾 Save Changes", command=save_changes, bootstyle="primary").grid(row=0, column=1, sticky="ew")
    ttk.Button(btn_frame, text="Cancel", command=lambda: modal.destroy(), bootstyle="secondary-outline").grid(row=0, column=0, sticky="ew", padx=(0, 6))


#  Tasks Page 
def show_tasks(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Tasks", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))

    btn_frame = ttk.Frame(frame)
    btn_frame.pack(fill="x", pady=(0, 8))
    ttk.Button(btn_frame, text="➕ Add Task",
               command=lambda: open_add_task_modal(user_id, username, frame)).pack(side="right", padx=(4, 0))
    ttk.Button(btn_frame, text="✏️ Edit Task",
               command=lambda: open_edit_task_modal(user_id, username, frame)).pack(side="right", padx=(0, 4))
    ttk.Button(btn_frame, text="🗑️ Delete Task",
               command=lambda: delete_task_action(user_id, username, frame),
               bootstyle="danger-outline").pack(side="right", padx=(0, 4))

    # Try to get full rows (with category and estimated time)
    try:
        rows_full = tasks.get_tasks_full_rows(username)
        if rows_full and len(rows_full[0]) >= 11:
            # (id, user_id, username, title, start_date, due_date, status, description, priority, category, estimated_minutes)
            rows = [[r[3], r[9], r[10], r[4], r[5], r[6]] for r in rows_full]
            columns = ["Title", "Category", "Est. Time (min)", "Start Date", "Due Date", "Status"]
        else:
            raise Exception("Fallback to basic rows")
    except Exception:
        rows = tasks.get_tasks_rows(username)
        columns = ["Title", "Start Date", "Due Date", "Status"]

    table = Tableview(master=frame, coldata=columns, rowdata=rows, paginated=False, searchable=True)
    table.pack(fill="both", expand=True, pady=(5, 0))
    frame.table = table


#  Admin Panel 
def show_admin_panel(user_id, username, frame):
    """
    Admin-only panel: list users, show/set/add/subtract EXP for debugging, and delete any user's tasks.
    """
    clear_frame(frame)
    ttk.Label(frame, text="Admin Panel", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))
    ttk.Label(frame, text="Manage user EXP and tasks (admin only).", font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w", pady=(0, 8))

    # Create tabbed interface
    notebook = ttk.Notebook(frame)
    notebook.pack(fill="both", expand=True, pady=(6, 0))

    # Tab 1: EXP Management
    exp_tab = ttk.Frame(notebook, padding=10)
    notebook.add(exp_tab, text="EXP Management")

    # User list
    ttk.Label(exp_tab, text="Select User").grid(row=0, column=0, sticky="w", pady=(6, 2))
    users = []
    try:
        with db.connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, username FROM users ORDER BY username")
            users = cur.fetchall()
    except Exception as e:
        print(f"[Admin] error fetching users: {e}")

    usernames_list = [u[1] for u in users] if users else []
    user_var = tk.StringVar()
    user_combo = ttk.Combobox(exp_tab, values=usernames_list, textvariable=user_var, state="readonly")
    user_combo.grid(row=1, column=0, sticky="ew", padx=(0, 12))
    if usernames_list:
        user_combo.set(usernames_list[0])

    # Display selected user's exp and level
    info_frame = ttk.Frame(exp_tab)
    info_frame.grid(row=1, column=1, sticky="nsew", padx=(12, 0))
    info_frame.columnconfigure(0, weight=1)

    exp_label = ttk.Label(info_frame, text="EXP: —")
    exp_label.pack(anchor="w")
    level_label = ttk.Label(info_frame, text="Level: —")
    level_label.pack(anchor="w")

    def refresh_selected_user_info(evt=None):
        sel = user_var.get()
        if not sel:
            exp_label.config(text="EXP: —")
            level_label.config(text="Level: —")
            return
        uid = None
        for u in users:
            if u[1] == sel:
                uid = u[0]
                break
        if uid is None:
            exp_label.config(text="EXP: —")
            level_label.config(text="Level: —")
            return
        r = db.get_reward_data(uid)
        exp_label.config(text=f"EXP: {r.get('exp', 0)}")
        level_label.config(text=f"Level: {r.get('level', 1)}")

    user_combo.bind("<<ComboboxSelected>>", refresh_selected_user_info)
    refresh_selected_user_info()

    # Amount entry
    ttk.Label(exp_tab, text="Amount (EXP)").grid(row=2, column=0, sticky="w", pady=(12, 0))
    amount_var = tk.StringVar()
    amount_entry = ttk.Entry(exp_tab, textvariable=amount_var)
    amount_entry.grid(row=3, column=0, sticky="ew")

    # Buttons: Add, Subtract, Set
    btns = ttk.Frame(exp_tab)
    btns.grid(row=3, column=1, sticky="w", padx=(12, 0))
    
    def admin_add_exp():
        sel = user_var.get()
        if not sel:
            Messagebox.show_error("Select a user first.")
            return
        try:
            amt = int(amount_var.get())
        except Exception:
            Messagebox.show_error("Enter a valid integer amount.")
            return
        uid = next((u[0] for u in users if u[1] == sel), None)
        if uid is None:
            Messagebox.show_error("User not found.")
            return
        res = db.add_exp(uid, amt)
        if res.get("success"):
            Messagebox.show_info(f"Added {amt} EXP to {sel}. New EXP: {res.get('exp')}")
            refresh_selected_user_info()
        else:
            Messagebox.show_error("Failed to add EXP.")

    def admin_subtract_exp():
        sel = user_var.get()
        if not sel:
            Messagebox.show_error("Select a user first.")
            return
        try:
            amt = int(amount_var.get())
        except Exception:
            Messagebox.show_error("Enter a valid integer amount.")
            return
        uid = next((u[0] for u in users if u[1] == sel), None)
        if uid is None:
            Messagebox.show_error("User not found.")
            return
        res = db.add_exp(uid, -abs(amt))
        if res.get("success"):
            Messagebox.show_info(f"Subtracted {amt} EXP from {sel}. New EXP: {res.get('exp')}")
            refresh_selected_user_info()
        else:
            Messagebox.show_error("Failed to subtract EXP.")

    def admin_set_exp():
        sel = user_var.get()
        if not sel:
            Messagebox.show_error("Select a user first.")
            return
        try:
            amt = int(amount_var.get())
            if amt < 0:
                Messagebox.show_error("EXP must be >= 0.")
                return
        except Exception:
            Messagebox.show_error("Enter a valid integer amount.")
            return
        uid = next((u[0] for u in users if u[1] == sel), None)
        if uid is None:
            Messagebox.show_error("User not found.")
            return
        ok = db.set_exp(uid, amt)
        if ok:
            Messagebox.show_info(f"Set {sel}'s EXP to {amt}.")
            refresh_selected_user_info()
        else:
            Messagebox.show_error("Failed to set EXP.")

    ttk.Button(btns, text="Add EXP", command=admin_add_exp, bootstyle="success-outline").pack(side="left", padx=(0,6))
    ttk.Button(btns, text="Subtract EXP", command=admin_subtract_exp, bootstyle="warning-outline").pack(side="left", padx=(0,6))
    ttk.Button(btns, text="Set EXP", command=admin_set_exp, bootstyle="secondary-outline").pack(side="left", padx=(0,6))

    # Tab 2: Task Management
    task_tab = ttk.Frame(notebook, padding=10)
    notebook.add(task_tab, text="Task Management")

    ttk.Label(task_tab, text="Manage Tasks for All Users", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 10))
    
    # User selection for task management
    user_task_frame = ttk.Frame(task_tab)
    user_task_frame.pack(fill="x", pady=(0, 10))
    
    ttk.Label(user_task_frame, text="Select User:").pack(side="left", padx=(0, 8))
    task_user_var = tk.StringVar()
    task_user_combo = ttk.Combobox(user_task_frame, values=usernames_list, textvariable=task_user_var, state="readonly", width=20)
    task_user_combo.pack(side="left", padx=(0, 12))
    if usernames_list:
        task_user_combo.set(usernames_list[0])
    
    def refresh_admin_tasks():
        selected_user = task_user_var.get()
        if not selected_user:
            return
        
        # Clear existing table
        for widget in task_display_frame.winfo_children():
            widget.destroy()
        
        # Get tasks for selected user
        try:
            rows_full = tasks.get_tasks_full_rows(selected_user)
            if rows_full and len(rows_full[0]) >= 11:
                rows = [[r[3], r[9], r[10], r[4], r[5], r[6]] for r in rows_full]
                columns = ["Title", "Category", "Est. Time (min)", "Start Date", "Due Date", "Status"]
            else:
                rows = tasks.get_tasks_rows(selected_user)
                columns = ["Title", "Start Date", "Due Date", "Status"]
        except Exception:
            rows = tasks.get_tasks_rows(selected_user)
            columns = ["Title", "Start Date", "Due Date", "Status"]
        
        if not rows:
            ttk.Label(task_display_frame, text=f"No tasks found for {selected_user}", foreground="#888").pack(pady=20)
            return
        
        table = Tableview(master=task_display_frame, coldata=columns, rowdata=rows, paginated=False, searchable=True, height=15)
        table.pack(fill="both", expand=True)
        task_display_frame.table = table
    
    ttk.Button(user_task_frame, text="🔄 Refresh", command=refresh_admin_tasks).pack(side="left", padx=(0, 12))
    
    # Delete button for admin
    def admin_delete_task():
        selected_user = task_user_var.get()
        if not selected_user:
            Messagebox.show_error("Please select a user first.")
            return
        
        table = getattr(task_display_frame, "table", None)
        if not table:
            Messagebox.show_error("No tasks loaded. Click Refresh first.")
            return
        
        selected = table.view.selection()
        if not selected:
            Messagebox.show_error("Please select a task to delete.")
            return
        
        selected_item = table.view.item(selected[0])["values"]
        if not selected_item:
            Messagebox.show_error("Invalid task data.")
            return
        
        # Support both formats
        if len(selected_item) >= 6:
            title = selected_item[0]
        elif len(selected_item) >= 4:
            title = selected_item[0]
        else:
            Messagebox.show_error("Invalid task data format.")
            return
        
        # Confirm deletion
        confirm = Messagebox.okcancel(
            f"Are you sure you want to delete '{title}' for user '{selected_user}'?\n\nThis action cannot be undone.",
            "Admin: Confirm Deletion"
        )
        
        if not confirm:
            return
        
        # Perform deletion
        success = tasks.safe_delete_task(selected_user, title)
        
        if success:
            Messagebox.show_info(f"Task deleted successfully for {selected_user}!")
            refresh_admin_tasks()
        else:
            Messagebox.show_error("Failed to delete task.")
    
    ttk.Button(user_task_frame, text="🗑️ Delete Selected Task", command=admin_delete_task, bootstyle="danger").pack(side="left")
    
    # Task display area
    task_display_frame = ttk.Frame(task_tab)
    task_display_frame.pack(fill="both", expand=True, pady=(10, 0))
    
    # Auto-cleanup section
    ttk.Separator(task_tab, orient="horizontal").pack(fill="x", pady=(15, 10))
    cleanup_frame = ttk.Frame(task_tab)
    cleanup_frame.pack(fill="x", pady=(5, 0))
    
    ttk.Label(cleanup_frame, text="Auto-Cleanup:", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 10))
    ttk.Label(cleanup_frame, text="Delete overdue tasks older than:").pack(side="left", padx=(0, 6))
    
    days_var = tk.StringVar(value="30")
    days_entry = ttk.Entry(cleanup_frame, textvariable=days_var, width=8)
    days_entry.pack(side="left", padx=(0, 6))
    ttk.Label(cleanup_frame, text="days").pack(side="left", padx=(0, 12))
    
    def run_auto_cleanup():
        try:
            days = int(days_var.get())
            if days < 1:
                Messagebox.show_error("Days must be at least 1.")
                return
        except Exception:
            Messagebox.show_error("Enter a valid number of days.")
            return
        
        confirm = Messagebox.okcancel(
            f"This will permanently delete all overdue (non-completed) tasks older than {days} days.\n\nContinue?",
            "Confirm Auto-Cleanup"
        )
        
        if not confirm:
            return
        
        result = tasks.auto_delete_overdue(days)
        if result.get("success"):
            deleted_count = result.get("deleted", 0)
            Messagebox.show_info(f"Auto-cleanup complete!\n\nDeleted {deleted_count} overdue task(s).")
            refresh_admin_tasks()
        else:
            Messagebox.show_error(f"Auto-cleanup failed: {result.get('error', 'Unknown error')}")
    
    ttk.Button(cleanup_frame, text="🧹 Run Cleanup", command=run_auto_cleanup, bootstyle="warning").pack(side="left")
    
    # Initial load
    refresh_admin_tasks()


#  Rewards Page
def show_rewards(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Rewards", font=("Segoe UI", 18, "bold")).pack(anchor="w", pady=(0, 10))

    reward = db.get_reward_data(user_id)
    exp = reward.get("exp", 0)
    level = reward.get("level", 1)
    avatar = reward.get("avatar", "female_1.png")

    # level text and progress
    ttk.Label(frame, text=f"Level {level} • {exp} EXP", font=("Segoe UI", 11)).pack(anchor="w", pady=(0, 6))
    progress_val = (exp % 100) / 100 * 100
    ttk.Progressbar(frame, value=progress_val, maximum=100).pack(fill="x", pady=(0, 12))

    # Equipped avatar large
    av_img = _load_avatar_thumbnail(avatar, size=(120, 120))
    av_frame = ttk.Frame(frame)
    av_frame.pack(fill="x", pady=(6, 12))
    if av_img:
        lbl = ttk.Label(av_frame, image=av_img)
        lbl.image = av_img
        lbl.pack(side="left", padx=(0, 12))
    ttk.Label(av_frame, text=f"Equipped: {avatar}", font=("Segoe UI", 11)).pack(anchor="w", side="left")

    # Thumbnails
    thumbs_frame = ttk.Frame(frame)
    thumbs_frame.pack(fill="x", pady=(8, 0))
    for fname, req_level in AVATAR_UNLOCKS:
        unlocked = level >= req_level
        img = _load_avatar_thumbnail(fname, size=(72, 72), greyscale=not unlocked)
        frm = ttk.Frame(thumbs_frame, padding=6)
        frm.pack(side="left", padx=6)
        if img:
            lbl = ttk.Label(frm, image=img)
            lbl.image = img
            lbl.pack()
        ttk.Label(frm, text=f"Lvl {req_level}", font=("Segoe UI", 8)).pack()
        if unlocked:
            btn = ttk.Button(frm, text="Equip", command=lambda f=fname: _equip_avatar(user_id, f, frame))
            btn.pack(pady=(6,0))
        else:
            ttk.Label(frm, text="Locked", font=("Segoe UI", 8), foreground="#888").pack(pady=(6,0))


def _equip_avatar(user_id, avatar_filename, parent_frame=None):
    ok = db.set_avatar(user_id, avatar_filename)
    if ok:
        Messagebox.show_info(f"Equipped {avatar_filename}")
        if parent_frame:
            try:
                for w in parent_frame.winfo_children():
                    w.destroy()
            except Exception:
                pass
    else:
        Messagebox.show_error("Failed to equip avatar.")


#  Settings 
def show_settings(user_id, username, frame):
    clear_frame(frame)
    ttk.Label(frame, text="Settings", font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(0, 12))
    ttk.Label(frame, text="Customize your experience here.", font=("Segoe UI", 10)).pack(anchor="w")

    # Avatar Customization panel
    ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=10)
    ttk.Label(frame, text="Avatar Customization", font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(8,6))

    reward = db.get_reward_data(user_id)
    level = reward.get("level", 1)
    current_avatar = reward.get("avatar", "female_1.png")

    grid = ttk.Frame(frame)
    grid.pack(fill="x", pady=(6, 0))

    for idx, (fname, req) in enumerate(AVATAR_UNLOCKS):
        col = idx % 6
        row = idx // 6
        card_frame = ttk.Frame(grid, padding=8, relief="flat")
        card_frame.grid(row=row, column=col, padx=6, pady=6)
        unlocked = level >= req
        img = _load_avatar_thumbnail(fname, size=(96, 96), greyscale=not unlocked)
        if img:
            lbl = ttk.Label(card_frame, image=img)
            lbl.image = img
            lbl.pack()

        ttk.Label(card_frame, text=fname, font=("Segoe UI", 9)).pack()
        ttk.Label(card_frame, text=f"Unlocks at Lvl {req}", font=("Segoe UI", 8), foreground="#666").pack()

        if unlocked:
            if fname == current_avatar:
                ttk.Label(card_frame, text="Equipped", font=("Segoe UI", 9, "bold")).pack(pady=(4,0))
            else:
                ttk.Button(card_frame, text="Equip", command=lambda f=fname: _on_equip_click(user_id, f, frame)).pack(pady=(6,0))
        else:
            ttk.Label(card_frame, text="Locked", foreground="#999").pack(pady=(6,0))


def _on_equip_click(user_id, fname, frame):
    ok = db.set_avatar(user_id, fname)
    if ok:
        Messagebox.show_info("Avatar equipped.")
        try:
            with db.connect() as conn:
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
                row = cur.fetchone()
                if row:
                    username = row[0]
                    show_settings(user_id, username, frame)
                    return
        except Exception:
            pass
        show_settings(user_id, "", frame)
    else:
        Messagebox.show_error("Failed to equip avatar.")


#  Analytics 
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


#  Timer Logic 
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


#  Overview 
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


#  Logout 
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
        root.geometry("1000x600")
        root.minsize(400, 400)
        root.title("Work Tracker — Login")

        # Reopen login window
        import login
        login.open_login_window(root)
    else:
        Messagebox.show_error("Logout failed. Please try again.", "Error")