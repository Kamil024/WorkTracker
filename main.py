import ttkbootstrap as ttk
from db import initialize_database
from auth import load_login_state
from dashboard import open_dashboard
from login import LoginWindow


def main():
    """Main entry point of the Work Tracker app."""
    initialize_database()

    # Initialize main app window
    app = ttk.Window(title="Work Tracker", themename="flatly")  # Light by default
    app.geometry("1000x600")
    app.minsize(900, 550)

    saved_user = load_login_state()
    if saved_user:
        open_dashboard(saved_user, app)
    else:
        LoginWindow(app)

    app.mainloop()



if __name__ == "__main__":
    main()


#TEST TEXT JUST  BECAUSE