import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from db import initialize_database
from auth import load_login_state
from dashboard import open_dashboard
from login import LoginWindow

#  LOADING SCREEN  #
class LoadingScreen(ttk.Toplevel):
    def __init__(self, master, on_complete):
        super().__init__(master)
        self.master = master
        self.on_complete = on_complete

        self.overrideredirect(True)  # Remove window border
        self.geometry("400x250+500+250")
        self.configure(bg="#ffffff")

        # Center content
        self.container = ttk.Frame(self, padding=20)
        self.container.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(
            self.container,
            text="WorkTracker",
            font=("Segoe UI Black", 28),
            foreground="#4B6EF5"
        ).pack(pady=(10, 5))

        ttk.Label(
            self.container,
            text="Preparing your workspace...",
            font=("Segoe UI", 12),
            foreground="#6B728E"
        ).pack(pady=(0, 20))

        # Progress bar
        self.progress = ttk.Progressbar(self.container, mode="indeterminate", bootstyle="info-striped")
        self.progress.pack(fill="x", pady=(10, 0))
        self.progress.start(10)

        # Fade-in animation
        self.attributes("-alpha", 0.0)
        self.fade_in(0)

        # Automatically close after a delay
        self.after(2500, self.close)

    def fade_in(self, value):
        if value <= 1.0:
            self.attributes("-alpha", value)
            self.after(40, self.fade_in, value + 0.1)

    def close(self):
        self.progress.stop()
        self.destroy()
        self.on_complete()  # Launch the main UI


#  MAIN APP  #
def main():
    initialize_database()

    # Create hidden root for the loading screen
    root = ttk.Window(title="Work Tracker", themename="flatly")
    root.withdraw()

    # Define what happens after the loading screen
    def start_app():
        root.deiconify()
        root.geometry("1000x600")
        root.minsize(900, 550)

        saved_user = load_login_state()
        if saved_user:
            open_dashboard(saved_user, root)
        else:
            LoginWindow(root)

    # Show loading splash
    LoadingScreen(root, on_complete=start_app)
    root.mainloop()


if __name__ == "__main__":
    main()
