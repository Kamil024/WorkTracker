import customtkinter as ctk
import db
from auth import load_login_state
from dashboard import open_dashboard
from login import show_startup

def initialize_database():
    """Create/upgrade DB schema safely with error handling."""
    try:
        db.create_user_table()
        db.create_task_table()
        db.migrate_schema_if_needed()
    except Exception as e:
        print(f"[DB ERROR] Failed to initialize database: {e}")

def main():
    """Main entry point of the Work Tracker app."""

    # Configure global appearance BEFORE app init for consistency
    ctk.set_appearance_mode("Dark")      # "Dark" | "Light" | "System"
    ctk.set_default_color_theme("blue")  # "blue" | "green" | "dark-blue"

    # Initialize database
    initialize_database()

    # Create main app window
    app = ctk.CTk()
    app.title("Work Tracker")
    app.geometry("1000x600")
    app.minsize(900, 550)

    # Auto-login if saved state exists and is valid
    saved_user = load_login_state()
    if saved_user:
        try:
            open_dashboard(saved_user, app)
        except Exception as e:
            print(f"[AUTH ERROR] Auto-login failed: {e}")
            show_startup(app)
    else:
        show_startup(app)

    app.mainloop()

if __name__ == "__main__":
    main()
