import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry
import db
from auth import logout
from datetime import datetime
from settings import load_theme_preference


def open_dashboard(username, app):
    theme = load_theme_preference()

    # Colors
    if theme == "dark":
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

    for w in app.winfo_children():
        w.destroy()
    app.configure(fg_color=bg_color)
    app.title(f"{username}'s Dashboard")
    app.geometry("1200x700")

    # SIDEBAR
    sidebar = ctk.CTkFrame(app, width=220, fg_color=sidebar_color, corner_radius=0)
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="Deadline", font=("Arial", 22, "bold"), text_color=button_fg_color).pack(pady=(30, 20))

    # MAIN PANEL container
    main = ctk.CTkFrame(app, fg_color=panel_color, corner_radius=12)
    main.pack(side="top", fill="both", expand=True, padx=40, pady=(30, 30))

    def clear_main():
        for w in main.winfo_children():
            w.destroy()

    # -------------------- Pages --------------------

    def show_overview():
        clear_main()
        ctk.CTkLabel(main, text="📊 Overview", font=("Arial", 20, "bold"), text_color=text_color).pack(pady=20)
        pending = db.get_tasks(username)
        done = db.get_completed_tasks(username)
        ctk.CTkLabel(main, text=f"Pending tasks: {len(pending)}", text_color=text_color).pack(pady=5)
        ctk.CTkLabel(main, text=f"Completed tasks: {len(done)}", text_color=text_color).pack(pady=5)

    def show_add_deadline():
        clear_main()

        # --- Tab buttons row ---
        tabs = ctk.CTkFrame(main, fg_color=panel_color)
        tabs.pack(fill="x", pady=5)
        for name in ["Edit Deadline", "Privacy Settings", "Alerts", "Set Reminder"]:
            ctk.CTkButton(tabs, text=name, fg_color="transparent",
                          text_color=text_color, hover_color="#ddd",
                          width=140).pack(side="left", padx=5)

        # --- Card form ---
        form = ctk.CTkFrame(main, fg_color=panel_color, border_width=1, corner_radius=10)
        form.pack(fill="both", expand=True, padx=30, pady=20)

        # Grid form layout
        fields = [
            ("Task Name", "Project Launch", 0, 0),
            ("Due Date", datetime.today().strftime("%Y-%m-%d"), 0, 1),
            ("Description", "Launch the new project.", 1, 0),
            ("Priority", "High", 2, 0),
            ("Notify Me", "1 day before", 2, 1),
            ("Category", "Work", 3, 0),
            ("Location", "Office", 3, 1),
            ("Status", "Pending", 4, 0),
            ("Notes", "Additional details here.", 4, 1),
        ]

        entries = {}
        for label, placeholder, r, c in fields:
            frame = ctk.CTkFrame(form, fg_color=panel_color)
            frame.grid(row=r, column=c, padx=20, pady=10, sticky="ew")
            ctk.CTkLabel(frame, text=label, text_color=text_color, anchor="w").pack(anchor="w")
            if label == "Due Date":
                entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
                entry.pack(fill="x")
            else:
                entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color=entry_bg_color, text_color=entry_fg_color)
                entry.pack(fill="x")
            entries[label] = entry

        def add_deadline():
            t = entries["Task Name"].get().strip()
            d = entries["Due Date"].get()
            if not t:
                messagebox.showwarning("Missing Task Name", "Please enter a task name.")
                return
            db.add_task(username, t, datetime.today().strftime("%Y-%m-%d"), d)
            messagebox.showinfo("Added", "Deadline added!")
            show_mytasks()

        ctk.CTkButton(form, text="Add Deadline", fg_color="black",
                      hover_color="#333", text_color="white", height=40,
                      command=add_deadline).grid(row=6, column=0, columnspan=2, pady=20, padx=30, sticky="ew")

    def show_upcoming():
        clear_main()
        ctk.CTkLabel(main, text="⏰ Upcoming Deadlines", font=("Arial", 20, "bold"), text_color=text_color).pack(pady=20)
        tasks = db.get_tasks(username)
        if not tasks:
            ctk.CTkLabel(main, text="No upcoming deadlines.", text_color="#888").pack()
            return
        for t in tasks:
            ctk.CTkLabel(main, text=f"{t[1]} — Due {t[3]}", text_color=text_color).pack(anchor="w", padx=20, pady=2)

    def show_mytasks():
        clear_main()
        ctk.CTkLabel(main, text="📝 My Tasks", font=("Arial", 20, "bold"), text_color=text_color).pack(pady=10)

        tasks = db.get_tasks(username)
        if not tasks:
            ctk.CTkLabel(main, text="No active tasks.", text_color="#888").pack(pady=20)
            return

        for t in tasks:
            card = ctk.CTkFrame(main, fg_color=panel_color, border_width=1, corner_radius=10)
            card.pack(fill="x", padx=30, pady=10)

            ctk.CTkLabel(card, text=f"{t[1]} (Due: {t[3]})", anchor="w", text_color=text_color,
                         font=("Arial", 15, "bold")).pack(side="left", padx=10, pady=10)

            # Buttons
            ctk.CTkButton(card, text="✅ Done", width=70,
                          command=lambda tid=t[0]: (db.update_task_completion(tid, 1), show_mytasks())
                          ).pack(side="right", padx=5, pady=10)
            ctk.CTkButton(card, text="❌ Delete", fg_color=danger_fg_color,
                          hover_color=danger_hover_color, width=70,
                          command=lambda tid=t[0]: (db.delete_task(tid), show_mytasks())
                          ).pack(side="right", padx=5, pady=10)

    def show_reports():
        clear_main()
        ctk.CTkLabel(main, text="📈 Progress Reports", font=("Arial", 20, "bold"), text_color=text_color).pack(pady=20)
        total = len(db.get_tasks(username)) + len(db.get_completed_tasks(username))
        done = len(db.get_completed_tasks(username))
        percent = (done / total * 100) if total else 0
        ctk.CTkLabel(main, text=f"Completed {done}/{total} tasks ({percent:.1f}%)", text_color=text_color).pack(pady=10)

    # -------------------- Sidebar Buttons --------------------
    nav_items = [
        ("📊 Overview", show_overview),
        ("➕ Add Deadline", show_add_deadline),
        ("⏰ Upcoming Deadlines", show_upcoming),
        ("📝 My Tasks", show_mytasks),
        ("📈 Progress Reports", show_reports),
    ]
    for text, cmd in nav_items:
        ctk.CTkButton(sidebar, text=text, anchor="w", fg_color="transparent",
                      hover_color="#d0d0d0", text_color=text_color,
                      font=("Arial", 15), command=cmd).pack(fill="x", padx=16, pady=2)

    # Footer
    ctk.CTkButton(sidebar, text="⚙️ Settings", anchor="w", fg_color="transparent",
                  hover_color="#d0d0d0", text_color=text_color, font=("Arial", 15)).pack(fill="x", padx=16, pady=(40, 2))
    ctk.CTkButton(sidebar, text="🚪 Log out", anchor="w", fg_color="transparent",
                  hover_color="#ffeaea", text_color=danger_fg_color, font=("Arial", 15),
                  command=lambda: (logout(), from_login())).pack(fill="x", padx=16, pady=2)

    # Default page
    show_overview()

    # Logout helper
    def from_login():
        from login import show_startup
        show_startup(app)
