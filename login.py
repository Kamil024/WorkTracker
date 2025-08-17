import customtkinter as ctk
from auth import login_user, register_user

def show_startup(app):
    # Clear the window first
    for widget in app.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(master=app)
    frame.pack(pady=60, padx=60, fill="both", expand=True)

    label = ctk.CTkLabel(master=frame, text="Work Tracker", font=("Arial", 20))
    label.pack(pady=12)

    username_entry = ctk.CTkEntry(master=frame, placeholder_text="Username")
    username_entry.pack(pady=6)

    password_entry = ctk.CTkEntry(master=frame, placeholder_text="Password", show="*")
    password_entry.pack(pady=6)

    keep_logged_in = ctk.CTkCheckBox(master=frame, text="Keep me logged in")
    keep_logged_in.pack(pady=6)

    def try_login():
        username = username_entry.get()
        password = password_entry.get()
        success, msg = login_user(username, password)
        if success:
            from dashboard import open_dashboard  # import here to avoid circular import
            if keep_logged_in.get():
                from auth import save_login_state
                save_login_state(username)
            open_dashboard(username, app)
        else:
            from tkinter import messagebox
            messagebox.showerror("Login Failed", msg)

    def try_register():
        username = username_entry.get()
        password = password_entry.get()
        success, msg = register_user(username, password)
        from tkinter import messagebox
        if success:
            messagebox.showinfo("Registration", msg)
        else:
            messagebox.showerror("Error", msg)

    login_button = ctk.CTkButton(master=frame, text="Login", command=try_login)
    login_button.pack(pady=6)

    register_button = ctk.CTkButton(master=frame, text="Register", command=try_register)
    register_button.pack(pady=6)

    footer = ctk.CTkLabel(master=frame, text="© 2025 Work Tracker", font=("Arial", 10))
    footer.pack(pady=10)
