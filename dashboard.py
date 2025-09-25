import customtkinter as ctk
from tkinter import messagebox
from tkcalendar import DateEntry, Calendar
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
        bg_color_panel = "#181a1f"  # darker for panels
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
        bg_color_panel = "#e0e0e0"  # gray for panels
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

        pending = len(db.get_tasks(username))
        completed = len(db.get_completed_tasks(username))
        total = pending + completed
        progress = f"{(completed / total * 100):.1f}%" if total else "0.0%"
        upcoming = pending  # Customize if you have separate logic

        # Panel 1: Pending Tasks
        panel1 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=220, height=640)
        panel1.place(x=0, y=0)
        panel1.pack_propagate(False)

        # Calendar UI (full month view)
        calendar_label = ctk.CTkLabel(panel1, text="Calendar", font=("Arial", 13), text_color=text_color)
        calendar_label.pack(pady=(30, 5))
        calendar = Calendar(panel1, selectmode="day", year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        calendar.pack(pady=(0, 10))

        # Panel 2: Completed Tasks
        panel2 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=670, height=200)
        panel2.place(x=230,y=0)
        panel2.pack_propagate(False)

        panel3 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=215, height=430)
        panel3.place(x=230,y=210)
        panel3.pack_propagate(False)

        panel4 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=215, height=430)
        panel4.place(x=455,y=210)
        panel4.pack_propagate(False)

        panel5 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=220, height=430)
        panel5.place(x=680,y=210)
        panel5.pack_propagate(False)

    def show_add_deadline():
        clear_main()

        # --- Tab buttons row ---
        tabs = ctk.CTkFrame(main, fg_color=panel_color)
        tabs.pack(fill="x", pady=5)
        for name in ["Add Task", "Edit Task", "Timer", "Set Reminder"]:
            ctk.CTkButton(tabs, text=name, fg_color="transparent",
                          text_color=text_color, hover_color="#ddd",
                          width=140).pack(side="left", padx=5)

        # --- Card form ---
        form = ctk.CTkFrame(main, fg_color=panel_color, border_width=1, corner_radius=10)
        form.pack(fill="both", expand=True, padx=30, pady=20)
        # Grid form layout (Start Date above Due Date, both in column 1)
        fields = [
            ("Task Name", "Project Launch", 0, 0),
            ("Start Date", datetime.today().strftime("%Y-%m-%d"), 0, 1),
            ("Due Date", datetime.today().strftime("%Y-%m-%d"), 1, 1),
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
            if label in ["Start Date", "Due Date"]:
                entry = DateEntry(frame, date_pattern="yyyy-mm-dd")
                entry.pack(fill="x")
            elif label == "Priority":
                priority_options = ["Low", "Medium", "High"]

                # Create an OptionMenu for the priority selection
                entry = ctk.CTkOptionMenu(
                    frame,
                    values=priority_options,
                    fg_color=entry_bg_color,
                    text_color=entry_fg_color,
                    dropdown_fg_color=entry_bg_color,
                    button_color=button_fg_color,
                    command=lambda choice: highlight_priority(choice)  # Handle the color change
                )
                entry.set("High")  # Default value
                entry.pack(fill="x")
                

            else:
                entry = ctk.CTkEntry(frame, placeholder_text=placeholder, fg_color=entry_bg_color, text_color=entry_fg_color)
                entry.pack(fill="x")
            entries[label] = entry

        def highlight_priority(priority):
            # Change the background color based on the priority
            if priority == "Low":
                entries["Priority"].configure(fg_color="#2ecc71")  # Green
            elif priority == "Medium":
                entries["Priority"].configure(fg_color="#f1c40f")  # Yellow
            else:  # High
                entries["Priority"].configure(fg_color="#e74c3c")  # Red

        def add_deadline():
            t = entries["Task Name"].get().strip()
            start = entries["Start Date"].get()
            due = entries["Due Date"].get()  # Ensure this gets a valid due date

            # Debugging: Print the collected values
            print(f"Task Name: {t}, Start Date: {start}, Due Date: {due}")  # Debugging output

            if not t:
                messagebox.showwarning("Missing Task Name", "Please enter a task name.")
                return

            # Ensure `due` is not empty or None
            if not due:
                messagebox.showwarning("Missing Due Date", "Please enter a due date.")
                return

            # Assuming `user_id` is available, for example, from your `db.get_user()` function
            user_id = 1  # Example user_id, replace with actual logic to retrieve user_id

            # Add the task
            try:
                db.add_task(user_id, username, t, start, due)  # Pass due_date properly
                messagebox.showinfo("Added", "Deadline added!")
            except ValueError as e:
                messagebox.showwarning("Error", str(e))  # Show if due_date is missing or invalid
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
        panel1 = ctk.CTkFrame(main, fg_color=bg_color_panel, corner_radius=10, width=905, height=640)
        panel1.place(x=0, y=0)
        panel1.pack_propagate(False)

        ctk.CTkLabel(panel1, text="📝 My Tasks", font=("Arial", 20, "bold"), text_color=text_color).pack(pady=10)
        tasks = db.get_tasks(username=username)

        if not tasks:
            ctk.CTkLabel(panel1, text="No active tasks.", text_color="#888").pack(pady=20)
            return

        for t in tasks:
            task_id, title, start_date, due_date, completed, status, priority, category, description, notes, notify = t

            card = ctk.CTkFrame(panel1, fg_color=panel_color, border_width=1, corner_radius=10)
            card.pack(fill="x", padx=30, pady=10)

            ctk.CTkLabel(card, text=f"{title} (Due: {due_date})", anchor="w", text_color=text_color,
                         font=("Arial", 15, "bold")).pack(anchor="w", padx=10, pady=(8, 0))

            info_text = f"Start: {start_date or 'N/A'} | Priority: {priority or 'N/A'} | Category: {category or 'N/A'} | Status: {status or 'Pending'}"
            ctk.CTkLabel(card, text=info_text, anchor="w", text_color="#888").pack(anchor="w", padx=10)

            if description:
                ctk.CTkLabel(card, text=f"📝 {description}", anchor="w", text_color="#aaa", wraplength=700).pack(anchor="w", padx=10, pady=(5, 0))
            if notes:
                ctk.CTkLabel(card, text=f"📌 {notes}", anchor="w", text_color="#888", wraplength=700).pack(anchor="w", padx=10, pady=(0, 5))

            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.pack(anchor="e", padx=10, pady=5)

            ctk.CTkButton(btn_frame, text="✅ Done", width=70,
                          command=lambda tid=task_id: (db.update_task_completion(tid, 1), show_mytasks())
                          ).pack(side="left", padx=5)
            ctk.CTkButton(btn_frame, text="❌ Delete", fg_color=danger_fg_color,
                          hover_color=danger_hover_color, width=70,
                          command=lambda tid=task_id: (db.delete_task(tid), show_mytasks())
                          ).pack(side="left", padx=5)


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
        ("➕ Activities", show_add_deadline),
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
