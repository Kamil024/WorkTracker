import os
import time
import customtkinter as ctk
from auth import login_user, register_user
from tkinter import messagebox
from PIL import Image
from settings import load_theme_preference, save_theme_preference

def show_startup(app):
    saved_theme = load_theme_preference()
    current_theme = {"mode": saved_theme}

    app.configure(fg_color="#f5f6fa" if saved_theme == "light" else "#2c3e50")

    for widget in app.winfo_children():
        widget.destroy()

    outer = ctk.CTkFrame(master=app, corner_radius=12, fg_color="white" if saved_theme == "light" else "#34495e")
    outer.pack(pady=50, padx=50, fill="both", expand=True)

    title_label = ctk.CTkLabel(
        outer, text="🗓 Work Tracker",
        font=("Arial", 24, "bold"),
        text_color="#2c3e50" if saved_theme == "light" else "white"
    )
    title_label.pack(pady=(15, 5))

    subtitle_label = ctk.CTkLabel(
        outer, text="Track that thang",
        font=("Arial", 12),
        text_color="#7f8c8d" if saved_theme == "light" else "#bdc3c7"
    )
    subtitle_label.pack(pady=(0, 15))

    username_entry = ctk.CTkEntry(
        outer, placeholder_text="Username", height=30, width=220,
        text_color="black" if saved_theme == "light" else "white",
        placeholder_text_color="#7f8c8d" if saved_theme == "light" else "#95a5a6"
    )
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(
        outer, placeholder_text="Password", show="*", height=30, width=220,
        text_color="black" if saved_theme == "light" else "white",
        placeholder_text_color="#7f8c8d" if saved_theme == "light" else "#95a5a6"
    )
    password_entry.pack(pady=5)

    keep_logged_in = ctk.CTkCheckBox(
        outer, text="Keep me logged in",
        text_color="#000" if saved_theme == "light" else "white"
    )
    keep_logged_in.pack(pady=5)

    def try_login():
        username, password = username_entry.get(), password_entry.get()
        success, msg = login_user(username, password)
        if success:
            from dashboard import open_dashboard
            if keep_logged_in.get():
                from auth import save_login_state
                save_login_state(username)
            open_dashboard(username, app)
        else:
            messagebox.showerror("Login Failed", msg)

    def try_register():
        username, password = username_entry.get(), password_entry.get()
        success, msg = register_user(username, password)
        if success:
            messagebox.showinfo("Registration", msg)
        else:
            messagebox.showerror("Error", msg)

    ctk.CTkButton(
        outer, text="Login", height=32, width=220,
        fg_color="#2980b9", hover_color="#3498db",
        command=try_login
    ).pack(pady=(10, 5))

    ctk.CTkButton(
        outer, text="Register", height=32, width=220,
        fg_color="#27ae60", hover_color="#2ecc71",
        command=try_register
    ).pack(pady=(0, 10))

    footer = ctk.CTkLabel(
        outer, text="© 2025 Work Tracker",
        font=("Arial", 9),
        text_color="#bdc3c7" if saved_theme == "light" else "#95a5a6"
    )
    footer.pack(pady=5)

    # --- Fixed part: Build absolute paths for icons ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    light_mode_path = os.path.join(BASE_DIR, "light-mode.png")  # Sun icon
    dark_mode_path = os.path.join(BASE_DIR, "dark-mode.png")    # Moon icon

    light_icon = ctk.CTkImage(Image.open(light_mode_path), size=(30, 30))
    dark_icon = ctk.CTkImage(Image.open(dark_mode_path), size=(30, 30))

    # Create toggle frame (the background slider track)
    toggle_frame = ctk.CTkFrame(outer, width=80, height=30, corner_radius=15,
                                fg_color="#ccc" if saved_theme == "light" else "#444")
    toggle_frame.pack(pady=10)

    # Slider circle that moves left/right on toggle
    slider_circle = ctk.CTkLabel(toggle_frame, image=dark_icon if saved_theme == "light" else light_icon,
                                 width=30, height=30, fg_color="white", corner_radius=15, text="")
    # Place initial slider position: left for dark mode, right for light mode
    slider_circle.place(relx=0.85 if saved_theme == "light" else 0.15, rely=0.5, anchor="center")

    def animate_slider(to_pos):
        steps = 10
        current_pos = slider_circle.place_info()
        current_relx = float(current_pos["relx"])
        delta = (to_pos - current_relx) / steps

        for _ in range(steps):
            current_relx += delta
            slider_circle.place(relx=current_relx, rely=0.5, anchor="center")
            app.update()
            time.sleep(0.02)

    def toggle_theme():
        if current_theme["mode"] == "light":
            # Switch to dark
            app.configure(fg_color="#2c3e50")
            outer.configure(fg_color="#34495e")
            title_label.configure(text_color="white")
            subtitle_label.configure(text_color="#bdc3c7")
            username_entry.configure(border_color="#7f8c8d", text_color="white", placeholder_text_color="#95a5a6")
            password_entry.configure(border_color="#7f8c8d", text_color="white", placeholder_text_color="#95a5a6")
            keep_logged_in.configure(text_color="white")
            footer.configure(text_color="#95a5a6")
            toggle_frame.configure(fg_color="#444")

            current_theme["mode"] = "dark"
            slider_circle.configure(image=light_icon)  # Sun icon for dark theme
            animate_slider(0.15)
            save_theme_preference("dark")

        else:
            # Switch to light
            app.configure(fg_color="#f5f6fa")
            outer.configure(fg_color="white")
            title_label.configure(text_color="#2c3e50")
            subtitle_label.configure(text_color="#7f8c8d")
            username_entry.configure(border_color="#ccc", text_color="black", placeholder_text_color="#7f8c8d")
            password_entry.configure(border_color="#ccc", text_color="black", placeholder_text_color="#7f8c8d")
            keep_logged_in.configure(text_color="#000")
            footer.configure(text_color="#bdc3c7")
            toggle_frame.configure(fg_color="#ccc")

            current_theme["mode"] = "light"
            slider_circle.configure(image=dark_icon)  # Moon icon for light theme
            animate_slider(0.85)
            save_theme_preference("light")

    # Clicking toggle_frame or slider_circle toggles theme
    toggle_frame.bind("<Button-1>", lambda e: toggle_theme())
    slider_circle.bind("<Button-1>", lambda e: toggle_theme())
