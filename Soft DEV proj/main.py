import customtkinter as ctk
import db
import auth
from login import show_startup
from dashboard import open_dashboard

# Set customtkinter appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def main():
    # Create users table in DB if not exists
    db.create_user_table()

    # Setup main window
    app = ctk.CTk()
    app.title("Work Tracker")
    app.geometry(f"{app.winfo_screenwidth()}x{app.winfo_screenheight()}+0+0")

    # Load saved login state (if any)
    saved_user = auth.load_login_state()

    # Route to dashboard or login page
    if saved_user:
        open_dashboard(saved_user, app)
    else:
        show_startup(app)

    app.mainloop()

if __name__ == "__main__":
    main()
