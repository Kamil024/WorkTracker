import customtkinter as ctk
from auth import login_user, register_user
from tkinter import messagebox

def show_startup(app):
    app.configure(fg_color="#f5f6fa")

    for widget in app.winfo_children():
        widget.destroy()

    outer = ctk.CTkFrame(master=app, corner_radius=12, fg_color="white")
    outer.pack(pady=50, padx=50, fill="both", expand=True)

    ctk.CTkLabel(
        outer, text="🗓 Work Tracker",
        font=("Arial", 24, "bold"), text_color="#2c3e50"
    ).pack(pady=(15, 5))

    ctk.CTkLabel(
        outer, text="Track that thang",
        font=("Arial", 12), text_color="#7f8c8d"
    ).pack(pady=(0, 15))

    username_entry = ctk.CTkEntry(outer, placeholder_text="Username", height=30, width=220)
    username_entry.pack(pady=5)

    password_entry = ctk.CTkEntry(outer, placeholder_text="Password", show="*", height=30, width=220)
    password_entry.pack(pady=5)

    keep_logged_in = ctk.CTkCheckBox(outer, text="Keep me logged in", text_color="#000")
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

    ctk.CTkLabel(
        outer, text="© 2025 Work Tracker",
        font=("Arial", 9), text_color="#bdc3c7"
    ).pack(pady=5)
