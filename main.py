# main.py
import ttkbootstrap as ttk
from db import initialize_database
from auth import load_login_state
from dashboard import open_dashboard
from login import LoginWindow

def main():
    """Main entry point of the Work Tracker app."""
    initialize_database()

    # Create main window
    app = ttk.Window(title="Work Tracker", themename="flatly")
    app.state("zoomed")  # start maximized
    app.minsize(900, 550)

    # Ensure layout stretches
    app.columnconfigure(0, weight=1)
    app.rowconfigure(0, weight=1)

    # Check for saved session
    saved_user = load_login_state()

    if saved_user:
        # Go straight to dashboard
        open_dashboard(saved_user, app)
    else:
        # Explicitly store reference so it's not garbage-collected
        login_screen = LoginWindow(app)
        login_screen.grid(row=0, column=0, sticky="nsew")

        # Make sure the gradient paints after window loads
        app.after(100, lambda: login_screen.on_resize(None))

    app.mainloop()


if __name__ == "__main__":
    main()
