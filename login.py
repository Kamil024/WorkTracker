import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, UnidentifiedImageError
from auth import login_user, register_user, save_login_state
from settings import load_theme_preference, save_theme_preference

def show_startup(app):
    """Display the login/register screen with theme support and safe icon handling."""

    # --- Load theme preference ---
    saved_theme = load_theme_preference()
    current_theme = {"mode": saved_theme}

    # Theme dictionaries
    light_theme = {
        "bg": "#ffffff", "card": "#ffffff", "text": "#111827", "subtitle": "#6b7280",
        "entry_fg": "#111827", "entry_bg": "#ffffff", "entry_border": "#d1d5db",
        "placeholder": "#6b7280", "checkbox": "#111827",
        "button_login": "#2563eb", "button_login_hover": "#1d4ed8",
        "button_register": "#22c55e", "button_register_hover": "#16a34a",
        "footer": "#6b7280", "icon": "🗓"
    }

    dark_theme = {
        "bg": "#181a20", "card": "#181a20", "text": "#f3f4f6", "subtitle": "#6b7280",
        "entry_fg": "#f3f4f6", "entry_bg": "#181a20", "entry_border": "#374151",
        "placeholder": "#6b7280", "checkbox": "#f3f4f6",
        "button_login": "#2563eb", "button_login_hover": "#1d4ed8",
        "button_register": "#22c55e", "button_register_hover": "#16a34a",
        "footer": "#6b7280", "icon": "🌙"
    }

    theme = light_theme if saved_theme == "light" else dark_theme
    app.configure(fg_color=theme["bg"])

    # Clear old widgets
    for widget in app.winfo_children():
        widget.destroy()

    # --- Main container ---
    outer = ctk.CTkFrame(master=app, corner_radius=16, fg_color=theme["card"])
    outer.pack(pady=60, padx=60, fill="both", expand=True)

    # Title
    title_label = ctk.CTkLabel(
        outer, text=f"{theme['icon']} Work Tracker",
        font=("Arial", 28, "bold"), text_color=theme["text"]
    )
    title_label.pack(pady=(30, 8))

    # Subtitle
    subtitle_label = ctk.CTkLabel(
        outer, text="Track that thang", font=("Arial", 14), text_color=theme["subtitle"]
    )
    subtitle_label.pack(pady=(0, 24))

    # Username / Password
    username_entry = ctk.CTkEntry(
        outer, placeholder_text="Username", height=48, width=340,
        fg_color=theme["entry_bg"], border_color=theme["entry_border"], border_width=2,
        text_color=theme["entry_fg"], placeholder_text_color=theme["placeholder"], font=("Arial", 14)
    )
    username_entry.pack(pady=8)

    password_entry = ctk.CTkEntry(
        outer, placeholder_text="Password", show="*", height=48, width=340,
        fg_color=theme["entry_bg"], border_color=theme["entry_border"], border_width=2,
        text_color=theme["entry_fg"], placeholder_text_color=theme["placeholder"], font=("Arial", 14)
    )
    password_entry.pack(pady=8)

    # Keep logged in
    keep_logged_in = ctk.CTkCheckBox(
        outer, text="Keep me logged in", text_color=theme["checkbox"], font=("Arial", 13)
    )
    keep_logged_in.pack(pady=(12, 18), anchor="center")

    # --- Logic ---
    def try_login():
        username, password = username_entry.get().strip(), password_entry.get()
        ok, msg, user = login_user(username, password)
        if ok:
            from dashboard import open_dashboard
            if keep_logged_in.get():
                save_login_state(username)
            open_dashboard(username, app)
        else:
            messagebox.showerror("Login Failed", msg)

    def try_register():
        username, password = username_entry.get().strip(), password_entry.get()
        ok, msg = register_user(username, password)
        if ok:
            messagebox.showinfo("Registration", msg)
        else:
            messagebox.showerror("Error", msg)

    app.bind('<Return>', lambda event: try_login())

    # Buttons
    ctk.CTkButton(
        outer, text="Login", height=48, width=340,
        fg_color=theme["button_login"], hover_color=theme["button_login_hover"],
        font=("Arial", 15, "bold"), command=try_login
    ).pack(pady=(0, 12))

    ctk.CTkButton(
        outer, text="Register", height=48, width=340,
        fg_color=theme["button_register"], hover_color=theme["button_register_hover"],
        font=("Arial", 15, "bold"), command=try_register
    ).pack(pady=(0, 18))

    # --- Test Button ---
    def open_test():
        # Import your db module and fetch all users
        import db
        users = db.get_all_users()  # You need to implement this in db.py
        if users:
            user_list = "\n".join([f"{u['username']} : {u['password']}" for u in users])
            messagebox.showinfo("All Users", user_list)
        else:
            messagebox.showinfo("All Users", "No users found.")

    ctk.CTkButton(
        outer, text="Test", height=48, width=340,
        fg_color="#8e44ad", hover_color="#9b59b6",
        font=("Arial", 15, "bold"), command=open_test
    ).pack(pady=(0, 18))

    # Footer
    footer = ctk.CTkLabel(
        outer, text="© 2025 Work Tracker", font=("Arial", 11), text_color=theme["footer"]
    )
    footer.pack(pady=(10, 0))

    # --- Theme Toggle (Top-right) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    light_icon_path = os.path.join(BASE_DIR, "light-mode.png")
    dark_icon_path  = os.path.join(BASE_DIR, "dark-mode.png")

    try:
        light_icon = ctk.CTkImage(Image.open(light_icon_path), size=(25, 25))
        dark_icon  = ctk.CTkImage(Image.open(dark_icon_path),  size=(25, 25))
    except (FileNotFoundError, UnidentifiedImageError):
        light_icon = dark_icon = None

    toggle_frame = ctk.CTkFrame(
        outer,
        width=70,
        height=28,
        corner_radius=14,
        fg_color="#dcdde1" if saved_theme == "light" else "#444",
        border_color="#111827" if saved_theme == "light" else "#f3f4f6",  # black for light, white for dark
        border_width=2
    )
    toggle_frame.place(relx=0.95, rely=0.05, anchor="ne")

    slider_circle = ctk.CTkLabel(toggle_frame,
                                 image=(dark_icon if saved_theme == "light" else light_icon),
                                 width=28, height=28, fg_color="white", corner_radius=14, text="")
    slider_circle.place(relx=0.8 if saved_theme == "light" else 0.2, rely=0.5, anchor="center")

    def toggle_theme():
        current_theme["mode"] = "dark" if current_theme["mode"] == "light" else "light"
        save_theme_preference(current_theme["mode"])
        # Re-render screen to apply new theme cleanly
        show_startup(app)

    def animate_toggle():
        # Animate slider_circle movement before toggling theme
        steps = 12
        start = 0.8 if current_theme["mode"] == "light" else 0.2
        end = 0.2 if current_theme["mode"] == "light" else 0.8
        delta = (end - start) / steps

        def step(i=0):
            pos = start + delta * i
            slider_circle.place(relx=pos, rely=0.5, anchor="center")
            if i < steps:
                toggle_frame.after(35, step, i + 1)  # 35ms per step for slower animation
            else:
                toggle_theme()

        step()

    toggle_frame.bind("<Button-1>", lambda e: animate_toggle())
    slider_circle.bind("<Button-1>", lambda e: animate_toggle())

