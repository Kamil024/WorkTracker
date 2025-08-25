import os
import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import db
from auth import logout
from datetime import datetime
from settings import load_theme_preference

# Optional: relative assets directory for the Overview mockup (kept; safe to ignore if not present)
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "frame0")


def open_dashboard(username, app):
    theme_mode = load_theme_preference()

    # Colors
    if theme_mode == "dark":
        bg_color = "#23272e"
        sidebar_color = "#1a1d22"
        panel_color = "#23272e"
        text_color = "white"
        entry_bg_color = "#23272e"
        entry_fg_color = "white"
        button_fg_color = "#2980b9"
        button_hover_color = "#3498db"
        danger_fg_color = "#c0392b"
        danger_hover_color = "#e74c3c"
        subtle_text = "#b7bdc7"
        hover_x = "#2c323b"
        card_blue = "#3498db"
        card_green = "#2ecc71"
        card_orange = "#e67e22"
        chart_pending = "#e74c3c"
        chart_done = "#2ecc71"
    else:
        bg_color = "#f7f7f7"
        sidebar_color = "#ededed"
        panel_color = "white"
        text_color = "#23272e"
        entry_bg_color = "white"
        entry_fg_color = "#23272e"
        button_fg_color = "#2980b9"
        button_hover_color = "#3498db"
        danger_fg_color = "#c0392b"
        danger_hover_color = "#e74c3c"
        subtle_text = "#5a6370"
        hover_x = "#d0d0d0"
        card_blue = "#3498db"
        card_green = "#2ecc71"
        card_orange = "#f39c12"
        chart_pending = "#e74c3c"
        chart_done = "#2ecc71"

    # Prepare app window
    for w in app.winfo_children():
        w.destroy()
    app.configure(fg_color=bg_color)
    app.title(f"{username}'s Dashboard")
    app.geometry("1200x700")
    app.minsize(1000, 640)

    # ---------- SIDEBAR (kept as-is) ----------
    sidebar = ctk.CTkFrame(app, width=220, fg_color=sidebar_color, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="Work Tracker", font=("Arial", 22, "bold"),
                 text_color=button_fg_color).pack(pady=(30, 20))

    # ---------- MAIN PANEL ----------
    main = ctk.CTkFrame(app, fg_color=panel_color, corner_radius=12)
    main.pack(side="top", fill="both", expand=True, padx=40, pady=(30, 30))

    def clear_main():
        for w in main.winfo_children():
            w.destroy()

    # ==================== PAGES ====================

    def show_overview():
        clear_main()

        # Header
        ctk.CTkLabel(main, text="Overview", font=("Arial", 22, "bold"),
                     text_color=text_color).pack(anchor="w", padx=24, pady=(6, 0))
        ctk.CTkLabel(main, text="Quick glance at your tasks and deadlines.",
                     font=("Arial", 12), text_color=subtle_text).pack(anchor="w", padx=24, pady=(0, 16))

        # Data
        active_tasks = db.get_tasks(username) or []            # (id, title, start_date, due_date, completed)
        completed_tasks = db.get_completed_tasks(username) or []
        total = len(active_tasks) + len(completed_tasks)
        done = len(completed_tasks)
        pending = len(active_tasks)
        pct = (done / total * 100) if total else 0.0

        # ---------- STAT CARDS ----------
        stats_frame = ctk.CTkFrame(main, fg_color=panel_color)
        stats_frame.pack(fill="x", padx=18, pady=(4, 6))

        def stat_card(parent, title, value, bg):
            card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=16)
            card.pack(side="left", padx=8, pady=8, expand=True, fill="both")
            ctk.CTkLabel(card, text=title, text_color="white", font=("Arial", 13, "bold")).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=str(value), text_color="white", font=("Arial", 22, "bold")).pack(pady=(0, 12))

        stat_card(stats_frame, "Total Tasks", total, card_blue)
        stat_card(stats_frame, "Completed", done, card_green)
        stat_card(stats_frame, "Pending", pending, card_orange)

        # ---------- BOTTOM SPLIT (Chart + Recent) ----------
        bottom = ctk.CTkFrame(main, fg_color=panel_color, corner_radius=16)
        bottom.pack(fill="both", expand=True, padx=18, pady=(10, 12))

        # Left: Chart
        chart_holder = ctk.CTkFrame(bottom, fg_color=panel_color)
        chart_holder.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        # Import matplotlib lazily and safely (won't crash if unavailable)
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

            fig, ax = plt.subplots(figsize=(3.3, 3.3), dpi=100)
            if total > 0:
                wedges, texts, autotexts = ax.pie(
                    [done, pending],
                    labels=["Completed", "Pending"],
                    autopct="%1.1f%%",
                    startangle=90,
                    colors=[chart_done, chart_pending],
                    wedgeprops={"linewidth": 0}
                )
                # Donut hole look
                centre_circle = plt.Circle((0, 0), 0.55, fc=panel_color)
                fig.gca().add_artist(centre_circle)
                ax.axis('equal')
            else:
                ax.text(0.5, 0.5, "No Data", ha="center", va="center", fontsize=13, color=subtle_text)
                ax.axis('off')

            ax.set_title("Task Completion", color=text_color)
            # Match figure background to CTk frame
            fig.patch.set_facecolor(panel_color)
            ax.set_facecolor(panel_color)

            canvas = FigureCanvasTkAgg(fig, master=chart_holder)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        except Exception:
            # Fallback if matplotlib not installed
            ctk.CTkLabel(chart_holder, text="(Install matplotlib to see the chart)",
                         text_color=subtle_text, font=("Arial", 13, "italic")).pack(pady=20)

        # Right: Recent Tasks
        recent_holder = ctk.CTkFrame(bottom, fg_color=panel_color)
        recent_holder.pack(side="right", fill="both", expand=True, padx=(8, 16), pady=16)

        ctk.CTkLabel(recent_holder, text="Recent Tasks",
                     font=("Arial", 16, "bold"), text_color=text_color).pack(anchor="w", pady=(0, 8))

        # Build a small recent list from both active and completed by newest id
        combined = active_tasks + completed_tasks
        # Sort descending by id (assuming AUTOINCREMENT increasing with time)
        combined.sort(key=lambda t: t[0], reverse=True)
        recent = combined[:5]

        if not recent:
            ctk.CTkLabel(recent_holder, text="No tasks yet.",
                         text_color=subtle_text, font=("Arial", 13, "italic")).pack(anchor="w")
        else:
            for t in recent:
                tid, title, start_date, due_date, completed = t
                due_txt = due_date if due_date else "No date"
                status_txt = "Completed" if completed else "Pending"
                ctk.CTkLabel(
                    recent_holder,
                    text=f"• {title}  —  Due: {due_txt}  [{status_txt}]",
                    text_color=text_color,
                    font=("Arial", 13)
                ).pack(anchor="w")

    def show_add_deadline():
        clear_main()

        tabs = ctk.CTkFrame(main, fg_color=panel_color)
        tabs.pack(fill="x", pady=5)
        for name in ["Edit Deadline", "Privacy Settings", "Alerts", "Set Reminder"]:
            ctk.CTkButton(
                tabs, text=name, fg_color="transparent",
                text_color=text_color, hover_color=hover_x, width=140
            ).pack(side="left", padx=5)

        form = ctk.CTkFrame(main, fg_color=panel_color, border_width=1, corner_radius=10)
        form.pack(fill="both", expand=True, padx=30, pady=20)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        def make_field(parent, label, r, c, placeholder=None, is_date=False):
            frame = ctk.CTkFrame(parent, fg_color=panel_color)
            frame.grid(row=r, column=c, padx=20, pady=10, sticky="ew")
            ctk.CTkLabel(frame, text=label, text_color=text_color, anchor="w").pack(anchor="w")
            if is_date:
                widget = DateEntry(frame, date_pattern="yyyy-mm-dd")
                widget.pack(fill="x")
            else:
                widget = ctk.CTkEntry(
                    frame, placeholder_text=(placeholder or ""),
                    fg_color=entry_bg_color, text_color=entry_fg_color
                )
                widget.pack(fill="x")
            return widget

        title_e = make_field(form, "Task Name", 0, 0, "Project Launch")
        due_e = make_field(form, "Due Date", 0, 1, is_date=True)
        start_e = make_field(form, "Start Date", 1, 0, is_date=True)
        make_field(form, "Notes (optional)", 1, 1, "Additional details")

        def add_deadline():
            t = title_e.get().strip()
            d = due_e.get()
            s = start_e.get()
            if not t:
                messagebox.showwarning("Missing Task Name", "Please enter a task name.")
                return
            try:
                # Use existing db API (no schema changes)
                db.add_task(username, t, s, d)
                messagebox.showinfo("Added", "Deadline added!")
                show_mytasks()
            except Exception as e:
                messagebox.showerror("DB Error", f"Failed to add deadline:\n{e}")

        ctk.CTkButton(
            form, text="Add Deadline", fg_color="black",
            hover_color="#333", text_color="white", height=40,
            command=add_deadline
        ).grid(row=3, column=0, columnspan=2, pady=20, padx=30, sticky="ew")

    def show_upcoming():
        clear_main()
        ctk.CTkLabel(main, text="⏰ Upcoming Deadlines", font=("Arial", 20, "bold"),
                     text_color=text_color).pack(pady=20)
        tasks = db.get_tasks(username) or []
        if not tasks:
            ctk.CTkLabel(main, text="No upcoming deadlines.", text_color=subtle_text).pack()
            return

        # Sort by due date ascending (unknowns last)
        def parse_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                return None

        tasks_sorted = sorted(tasks, key=lambda t: (parse_date(t[3]) is None, parse_date(t[3]) or datetime.max))

        for t in tasks_sorted:
            _, title, start, due, _ = t
            txt = f"{title} — Due {due or 'N/A'}"
            ctk.CTkLabel(main, text=txt, text_color=text_color).pack(anchor="w", padx=20, pady=2)

    def show_mytasks():
        clear_main()
        ctk.CTkLabel(main, text="📝 My Tasks", font=("Arial", 20, "bold"),
                     text_color=text_color).pack(pady=10)

        tasks = db.get_tasks(username) or []
        if not tasks:
            ctk.CTkLabel(main, text="No active tasks.", text_color=subtle_text).pack(pady=20)
            return

        # Sort by due date (soonest first)
        def parse_date(s):
            try:
                return datetime.strptime(s, "%Y-%m-%d")
            except Exception:
                return None

        tasks_sorted = sorted(tasks, key=lambda t: (parse_date(t[3]) is None, parse_date(t[3]) or datetime.max))

        for t in tasks_sorted:
            tid, title, start, due, completed = t
            card = ctk.CTkFrame(main, fg_color=panel_color, border_width=1, corner_radius=10)
            card.pack(fill="x", padx=30, pady=10)

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=10, pady=10)

            ctk.CTkLabel(left, text=f"{title} (Due: {due or 'N/A'})",
                         anchor="w", text_color=text_color,
                         font=("Arial", 15, "bold")).pack(anchor="w")
            meta = f"Start: {start or '—'}"
            ctk.CTkLabel(left, text=meta, text_color=subtle_text, font=("Arial", 12)).pack(anchor="w")

            # Buttons
            ctk.CTkButton(
                card, text="✅ Done", width=70,
                command=lambda task_id=tid: (db.update_task_completion(task_id, 1), show_mytasks())
            ).pack(side="right", padx=5, pady=10)

            ctk.CTkButton(
                card, text="❌ Delete", fg_color=danger_fg_color,
                hover_color=danger_hover_color, width=70,
                command=lambda task_id=tid: (db.delete_task(task_id), show_mytasks())
            ).pack(side="right", padx=5, pady=10)

    def show_reports():
        clear_main()
        ctk.CTkLabel(main, text="📈 Progress Reports", font=("Arial", 20, "bold"),
                     text_color=text_color).pack(pady=20)
        active = db.get_tasks(username) or []
        done = db.get_completed_tasks(username) or []
        total = len(active) + len(done)
        pct = (len(done) / total * 100) if total else 0.0

        # Overdue = active with due_date < today
        today_str = datetime.today().strftime("%Y-%m-%d")
        overdue = [t for t in active if (t[3] and t[3] < today_str)]

        ctk.CTkLabel(main, text=f"Completed {len(done)}/{total} tasks ({pct:.1f}%)",
                     text_color=text_color).pack(pady=10)
        ctk.CTkLabel(main, text=f"Overdue: {len(overdue)}", text_color=danger_fg_color,
                     font=("Arial", 14, "bold")).pack(pady=4)

    # ---------- Sidebar Buttons (kept) ----------
    active_btn = {"ref": None}

    def make_nav_button(text, cmd):
        def wrapped():
            if active_btn["ref"]:
                active_btn["ref"].configure(fg_color="transparent")
            btn.configure(fg_color=hover_x)
            active_btn["ref"] = btn
            cmd()
        btn = ctk.CTkButton(
            sidebar, text=text, anchor="w", fg_color="transparent",
            hover_color=hover_x, text_color=text_color, font=("Arial", 15), command=wrapped
        )
        btn.pack(fill="x", padx=16, pady=2)
        return btn

    nav = [
        ("📊 Overview", show_overview),
        ("➕ Add Deadline", show_add_deadline),
        ("⏰ Upcoming Deadlines", show_upcoming),
        ("📝 My Tasks", show_mytasks),
        ("📈 Progress Reports", show_reports),
    ]
    for text, cmd in nav:
        make_nav_button(text, cmd)

    # Footer
    ctk.CTkButton(sidebar, text="⚙️ Settings", anchor="w", fg_color="transparent",
                  hover_color=hover_x, text_color=text_color, font=("Arial", 15)).pack(
        fill="x", padx=16, pady=(40, 2)
    )

    def from_login():
        from login import show_startup
        show_startup(app)

    ctk.CTkButton(sidebar, text="🚪 Log out", anchor="w", fg_color="transparent",
                  hover_color="#ffeaea", text_color=danger_fg_color, font=("Arial", 15),
                  command=lambda: (logout(), from_login())).pack(fill="x", padx=16, pady=2)

    # Default page
    show_overview()
