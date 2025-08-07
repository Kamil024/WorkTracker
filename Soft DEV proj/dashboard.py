# dashboard.py
import customtkinter as ctk
import os

def open_dashboard(username, app):
    # Clear all widgets in the main app window
    for widget in app.winfo_children():
        widget.destroy()

    frame = ctk.CTkFrame(master=app)
    frame.pack(pady=60, padx=60, fill="both", expand=True)

    label = ctk.CTkLabel(master=frame, text=f"Welcome, {username}!", font=("Arial", 20))
    label.pack(pady=20)

    logout_button = ctk.CTkButton(master=frame, text="Logout", command=lambda: logout(app))
    logout_button.pack(pady=10)


def logout(app):
    # Remove login state if exists
    try:
        os.remove("login_state.txt")
    except FileNotFoundError:
        pass

    # Clear all widgets in the app
    for widget in app.winfo_children():
        widget.destroy()

    # Go back to login screen
    from login import show_startup
    show_startup(app)
