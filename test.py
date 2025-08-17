import customtkinter as ctk

def open_dashboard(app):
    # Set the theme and colors (dark theme as an example)
    bg_color = "#181a20"  # Dark background
    panel_color = "#2c3e50"  # Dark panel background
    text_color = "white"  # White text for dark mode
    border_color = "#34495e"  # Border color for panels

    # Clear any existing widgets
    for w in app.winfo_children():
        w.destroy()

    app.configure(fg_color=bg_color)
    app.title("Dashboard")
    app.geometry("1200x700")

    # Panel 1 (P1) - Left sidebar with border
    left = ctk.CTkFrame(app, width=300, fg_color=panel_color, corner_radius=12, border_width=2, border_color=border_color)
    left.pack(side="left", fill="y", padx=16, pady=16)

    # Panel 2 (P2) - Main content area with border
    right = ctk.CTkFrame(app, fg_color=panel_color, corner_radius=12, border_width=2, border_color=border_color)
    right.pack(side="right", fill="both", expand=True, padx=16, pady=(16, 0))  # Panel 2 - Main content area

    # Panel 3 (P3) - Inside Panel 2, below the main content
    bottom_panel = ctk.CTkFrame(right, fg_color=panel_color, corner_radius=12, border_width=2, border_color=border_color)
    bottom_panel.pack(side="bottom", fill="x", padx=16, pady=(20, 16))  # Panel 3 - Bottom of P2

    # Labels inside each panel for demonstration
    ctk.CTkLabel(left, text="Panel 1 (Left Sidebar)", font=("Arial", 14, "bold"), text_color=text_color).pack(pady=20)
    ctk.CTkLabel(right, text="Panel 2 (Main Area)", font=("Arial", 14, "bold"), text_color=text_color).pack(pady=20)
    ctk.CTkLabel(bottom_panel, text="Panel 3 (Inside Panel 2)", font=("Arial", 14, "bold"), text_color=text_color).pack(pady=20)

# Initialize the app
if __name__ == "__main__":
    app = ctk.CTk()
    open_dashboard(app)
    app.mainloop()
