import customtkinter as ctk
import db
from auth import load_login_state
from dashboard import open_dashboard
from login import show_startup

def main():
    # Initialize DB tables
    db.create_user_table()
    db.create_task_table()

    # Create main app window
    app = ctk.CTk()
    app.title("Work Tracker")
    app.geometry("1000x600")
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    # Auto-login if saved state exists
    saved_user = load_login_state()
    if saved_user:
        open_dashboard(saved_user, app)  # Pass existing app window
    else:
        show_startup(app)

    app.mainloop()

if __name__ == "__main__":
    main()
