# login.py
import os
import time
import customtkinter as ctk
from auth import login_user, register_user, save_login_state
from tkinter import messagebox
from PIL import Image
from settings import load_theme_preference, save_theme_preference

def show_startup(app):
    saved_theme = load_theme_preference()
    current_theme = {"mode": saved_theme}

    # --- Colors for modern UI ---
    if saved_theme == "light":
        bg_color = "#ffffff"
        card_color = "#ffffff"
        text_color = "#111827"
        subtitle_color = "#6b7280"
        entry_fg = "#111827"
        entry_bg = "#ffffff"
        entry_border = "#d1d5db"
        placeholder_color = "#6b7280"
        checkbox_color = "#111827"
        button_login = "#2563eb"
        button_login_hover = "#1d4ed8"
        button_register = "#22c55e"
        button_register_hover = "#16a34a"
        footer_color = "#6b7280"
        icon = "🗓"
    else:
        bg_color = "#181a20"
        card_color = "#181a20"
        text_color = "#f3f4f6"
        subtitle_color = "#6b7280"
        entry_fg = "#f3f4f6"
        entry_bg = "#181a20"
        entry_border = "#374151"
        placeholder_color = "#6b7280"
        checkbox_color = "#f3f4f6"
        button_login = "#2563eb"
        button_login_hover = "#1d4ed8"
        button_register = "#22c55e"
        button_register_hover = "#16a34a"
        footer_color = "#6b7280"
        icon = "🌙"

    app.configure(fg_color=bg_color)

    for widget in app.winfo_children():
        widget.destroy()

    outer = ctk.CTkFrame(
        master=app,
        corner_radius=16,
        fg_color=card_color,
        border_width=0,
    )
    outer.pack(pady=60, padx=60, fill="both", expand=True)

    # Title with icon
    title_label = ctk.CTkLabel(
        outer,
        text=f"{icon} Work Tracker",
        font=("Arial", 28, "bold"),
        text_color=text_color,
    )
    title_label.pack(pady=(30, 8))

    # Subtitle
    subtitle_label = ctk.CTkLabel(
        outer,
        text="Track that thang",
        font=("Arial", 14),
        text_color=subtitle_color,
    )
    subtitle_label.pack(pady=(0, 24))

    # Username field
    username_entry = ctk.CTkEntry(
        outer,
        placeholder_text="Username",
        height=48,
        width=340,
        fg_color=entry_bg,
        border_color=entry_border,
        border_width=2,
        text_color=entry_fg,
        placeholder_text_color=placeholder_color,
        font=("Arial", 14)
    )
    username_entry.pack(pady=8)

    # Password field
    password_entry = ctk.CTkEntry(
        outer,
        placeholder_text="Password",
        show="*",
        height=48,
        width=340,
        fg_color=entry_bg,
        border_color=entry_border,
        border_width=2,
        text_color=entry_fg,
        placeholder_text_color=placeholder_color,
        font=("Arial", 14)
    )
    password_entry.pack(pady=8)

    # Checkbox
    keep_logged_in = ctk.CTkCheckBox(
        outer,
        text="Keep me logged in",
        text_color=checkbox_color,
        font=("Arial", 13)
    )
    keep_logged_in.pack(pady=(12, 18), anchor="center")

    # --- Login/Register logic ---
    def try_login():
        username, password = username_entry.get(), password_entry.get()
        success, msg = login_user(username, password)
        if success:
            from dashboard import open_dashboard
            if keep_logged_in.get():
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

    # Bind Enter key to login
    app.bind('<Return>', lambda event: try_login())

    # Login Button
    ctk.CTkButton(
        outer,
        text="Login",
        height=48,
        width=340,
        fg_color=button_login,
        hover_color=button_login_hover,
        font=("Arial", 15, "bold"),
        command=try_login
    ).pack(pady=(0, 12))

    # Register Button
    ctk.CTkButton(
        outer,
        text="Register",
        height=48,
        width=340,
        fg_color=button_register,
        hover_color=button_register_hover,
        font=("Arial", 15, "bold"),
        command=try_register
    ).pack(pady=(0, 18))


























    

    # ----------- TEST BUTTON (ADDED BUTTON) -----------
    def open_test():
        # Define the path to the test.py file
        test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test.py')  # Ensure test.py is in the same folder
        
        if os.path.exists(test_file_path):  # Check if test.py exists in the path
            os.system(f'python {test_file_path}')  # Run test.py using python
        else:
            messagebox.showerror("File Not Found", "The test.py file was not found.")  # Show an error if the file is missing

    # Add a new "Test" button
    ctk.CTkButton(
        outer,
        text="Test",  # Button label
        height=48,
        width=340,
        fg_color="#8e44ad",  # Button color
        hover_color="#9b59b6",  # Hover color
        font=("Arial", 15, "bold"),
        command=open_test  # Link the button to the function
    ).pack(pady=(0, 18))  # Add padding between this and other elements
    # ----------- END OF TEST BUTTON -----------





































    # Footer (Fixed Indentation)
    footer = ctk.CTkLabel(
        outer,
        text="© 2025 Work Tracker",
        font=("Arial", 11),
        text_color=footer_color,
    )
    footer.pack(pady=(10, 0))

    # --- Theme Toggle (Upper Right Corner) ---
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    light_mode_path = os.path.join(BASE_DIR, "light-mode.png")  # Sun icon
    dark_mode_path = os.path.join(BASE_DIR, "dark-mode.png")    # Moon icon

    light_icon = ctk.CTkImage(Image.open(light_mode_path), size=(25, 25))
    dark_icon = ctk.CTkImage(Image.open(dark_mode_path), size=(25, 25))

    toggle_frame = ctk.CTkFrame(
        outer, width=70, height=28, corner_radius=14,
        fg_color="#dcdde1" if saved_theme == "light" else "#444"
    )
    toggle_frame.place(relx=0.95, rely=0.05, anchor="ne")

    slider_circle = ctk.CTkLabel(
        toggle_frame,
        image=dark_icon if saved_theme == "light" else light_icon,
        width=28, height=28,
        fg_color="white", corner_radius=14, text=""
    )
    slider_circle.place(relx=0.8 if saved_theme == "light" else 0.2, rely=0.5, anchor="center")

    # Smooth animation
    def animate_slider(to_pos):
        steps = 10
        current_pos = slider_circle.place_info()
        current_relx = float(current_pos["relx"])
        delta = (to_pos - current_relx) / steps
        for _ in range(steps):
            current_relx += delta
            slider_circle.place(relx=current_relx, rely=0.5, anchor="center")
            app.update()
            time.sleep(0.015)

    # Toggle logic
    def toggle_theme():
        nonlocal icon
        if current_theme["mode"] == "light":
            # Dark mode
            app.configure(fg_color="#181a20")
            outer.configure(fg_color="#181a20")
            title_label.configure(text_color="#f3f4f6", text="🌙 Work Tracker")
            subtitle_label.configure(text_color="#6b7280")
            username_entry.configure(
                fg_color="#181a20", border_color="#374151", text_color="#f3f4f6", placeholder_text_color="#6b7280"
            )
            password_entry.configure(
                fg_color="#181a20", border_color="#374151", text_color="#f3f4f6", placeholder_text_color="#6b7280"
            )
            keep_logged_in.configure(text_color="#f3f4f6")
            footer.configure(text_color="#6b7280")
            toggle_frame.configure(fg_color="#444")

            current_theme["mode"] = "dark"
            slider_circle.configure(image=light_icon)
            animate_slider(0.2)
            save_theme_preference("dark")

        else:
            # Light mode
            app.configure(fg_color="#ffffff")
            outer.configure(fg_color="#ffffff")
            title_label.configure(text_color="#111827", text="🗓 Work Tracker")
            subtitle_label.configure(text_color="#6b7280")
            username_entry.configure(
                fg_color="#ffffff", border_color="#d1d5db", text_color="#111827", placeholder_text_color="#6b7280"
            )
            password_entry.configure(
                fg_color="#ffffff", border_color="#d1d5db", text_color="#111827", placeholder_text_color="#6b7280"
            )
            keep_logged_in.configure(text_color="#111827")
            footer.configure(text_color="#6b7280")
            toggle_frame.configure(fg_color="#dcdde1")

            current_theme["mode"] = "light"
            slider_circle.configure(image=dark_icon)
            animate_slider(0.8)
            save_theme_preference("light")

    # Make it clickable
    toggle_frame.bind("<Button-1>", lambda e: toggle_theme())
    slider_circle.bind("<Button-1>", lambda e: toggle_theme())
