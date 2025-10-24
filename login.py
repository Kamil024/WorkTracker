import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Canvas, font as tkFont, W, X
import auth
from dashboard import open_dashboard

class LoginWindow(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.username_var = ttk.StringVar()
        self.password_var = ttk.StringVar()
        self.name_var = ttk.StringVar()
        self.is_signup = False

        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        # Gradient background
        self.gradient = Canvas(self.master, highlightthickness=0)
        self.gradient.grid(row=0, column=0, sticky="nsew")

        # Container
        self.container = ttk.Frame(self.master)
        self.container.grid(row=0, column=0, sticky="nsew")
        self.container.columnconfigure(0, weight=1)
        self.container.rowconfigure(0, weight=1)

        # Main frame
        self.main_frame = ttk.Frame(self.container)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.92, relheight=0.88)
        self.main_frame.columnconfigure(0, weight=1, uniform="col")
        self.main_frame.columnconfigure(1, weight=1, uniform="col")
        self.main_frame.rowconfigure(0, weight=1)

        self.create_styles()
        self.build_ui()

        # Responsive behavior only
        self.master.bind("<Configure>", self.on_resize)

        # Bind Enter key only for login mode
        self.bind_enter_key()

    # ---------------------- STYLES ----------------------
    def create_styles(self):
        self.base_fonts = {
            "title": tkFont.Font(family="Segoe UI Semibold", size=28),
            "subtitle": tkFont.Font(family="Segoe UI", size=12),
            "feature": tkFont.Font(family="Segoe UI Semibold", size=12),
            "gray": tkFont.Font(family="Segoe UI", size=10),
            "entry": tkFont.Font(family="Segoe UI", size=10),
            "button": tkFont.Font(family="Segoe UI Semibold", size=10),
        }

        style = ttk.Style()
        style.configure("Title.TLabel", font=self.base_fonts["title"], foreground="#212121")
        style.configure("Subtitle.TLabel", font=self.base_fonts["subtitle"], foreground="#6B728E")
        style.configure("Feature.TLabel", font=self.base_fonts["feature"])
        style.configure("Gray.TLabel", font=self.base_fonts["gray"], foreground="#9CA3AF")
        style.configure("Custom.TEntry", padding=6, relief="flat", font=self.base_fonts["entry"])
        style.configure("Primary.TButton", font=self.base_fonts["button"], padding=8)
        style.configure("Card.TFrame", background="white", relief="flat")

    # ---------------------- BUILD UI ----------------------
    def build_ui(self):
        # LEFT PANEL
        left = ttk.Frame(self.main_frame)
        left.grid(row=0, column=0, sticky="nsew", padx=(40, 20), pady=30)
        left.columnconfigure(0, weight=1)

        self.brand_label = ttk.Label(left, text="WorkTracker Pro", font=("Segoe UI Black", 34), foreground="#4B6EF5")
        self.brand_label.pack(pady=(20, 10))

        self.brand_sub = ttk.Label(
            left,
            text="Stay productive, stay organized, and achieve your goals effortlessly.",
            style="Subtitle.TLabel",
            wraplength=380,
            justify="center",
        )
        self.brand_sub.pack(pady=(0, 30))

        features = [
            ("🕒 Smart Timer", "Boost focus with adaptive Pomodoro cycles."),
            ("✅ Task Priority", "Track what matters most."),
            ("📊 Analytics", "Visualize your progress over time."),
        ]
        for title, desc in features:
            box = ttk.Frame(left, padding=8)
            box.pack(fill=X, padx=10, pady=8)
            ttk.Label(box, text=title, style="Feature.TLabel").pack(anchor=W)
            ttk.Label(box, text=desc, style="Gray.TLabel").pack(anchor=W)

        # RIGHT PANEL (login card)
        right = ttk.Frame(self.main_frame)
        right.grid(row=0, column=1, sticky="nsew", padx=(20, 40), pady=30)
        right.columnconfigure(0, weight=1)

        self.card = ttk.Frame(right, padding=28, style="Card.TFrame")
        self.card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.8, relheight=0.75)
        self.card.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(self.card, text="Welcome Back 👋", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, pady=(0, 6))

        self.subtitle_label = ttk.Label(self.card, text="Sign in to continue to WorkTracker", style="Subtitle.TLabel")
        self.subtitle_label.grid(row=1, column=0, pady=(0, 20))

        # Dynamic field section
        self.fields_frame = ttk.Frame(self.card)
        self.fields_frame.grid(row=2, column=0, sticky="ew")
        self.fields_frame.columnconfigure(0, weight=1)

        # Build default login fields
        self.build_login_fields()

        ttk.Label(self.card, text="✨ Stay signed in for faster access", style="Gray.TLabel").grid(row=6, column=0, pady=(16, 0))

    def build_login_fields(self):
        """Create the input fields depending on mode."""
        for widget in self.fields_frame.winfo_children():
            widget.destroy()

        if self.is_signup:
            ttk.Label(self.fields_frame, text="Full Name").grid(row=0, column=0, sticky=W)
            ttk.Entry(self.fields_frame, textvariable=self.name_var, width=36, style="Custom.TEntry").grid(row=1, column=0, pady=(4, 10))

        ttk.Label(self.fields_frame, text="Username").grid(row=2, column=0, sticky=W)
        self.username_entry = ttk.Entry(self.fields_frame, textvariable=self.username_var, width=36, style="Custom.TEntry")
        self.username_entry.grid(row=3, column=0, pady=(4, 12))

        ttk.Label(self.fields_frame, text="Password").grid(row=4, column=0, sticky=W)
        self.password_entry = ttk.Entry(self.fields_frame, textvariable=self.password_var, width=36, show="•", style="Custom.TEntry")
        self.password_entry.grid(row=5, column=0, pady=(4, 18))

        # Focus cursor in username field by default
        self.username_entry.focus_set()

        btn_text = "Sign Up" if self.is_signup else "Sign In"
        self.sign_in_btn = ttk.Button(self.fields_frame, text=btn_text, bootstyle="PRIMARY", width=26, command=self.handle_auth)
        self.sign_in_btn.grid(row=6, column=0, pady=(0, 10))

        switch_text = "Back to Login" if self.is_signup else "Create an Account"
        self.switch_button = ttk.Button(self.fields_frame, text=switch_text, bootstyle="SECONDARY", width=26, command=self.toggle_mode)
        self.switch_button.grid(row=7, column=0)

    # ---------------------- RESPONSIVE BEHAVIOR ----------------------
    def draw_gradient(self, w, h):
        self.gradient.delete("gradient")
        color_top = (80, 120, 250)
        color_bot = (165, 95, 200)
        steps = max(h, 2)
        for i in range(steps):
            r = int(color_top[0] + (color_bot[0] - color_top[0]) * (i / steps))
            g = int(color_top[1] + (color_bot[1] - color_top[1]) * (i / steps))
            b = int(color_top[2] + (color_bot[2] - color_top[2]) * (i / steps))
            color = f"#{r:02x}{g:02x}{b:02x}"
            self.gradient.create_line(0, i, w, i, fill=color, tags="gradient")
        self.gradient.lower("gradient")

    def on_resize(self, event):
        w, h = self.master.winfo_width(), self.master.winfo_height()
        if w <= 0 or h <= 0:
            return

        if self.gradient.winfo_exists():
            self.gradient.config(width=w, height=h)
            self.draw_gradient(w, h)

        scale = max(0.6, min(1.5, w / 1100))
        for key, base_font in self.base_fonts.items():
            size_map = {
                "title": 28, "subtitle": 12, "feature": 12,
                "gray": 10, "entry": 10, "button": 10
            }
            base_font.configure(size=int(size_map[key] * scale))

        if hasattr(self, "brand_label") and self.brand_label.winfo_exists():
            self.brand_label.configure(font=("Segoe UI Black", int(34 * scale)))

        if hasattr(self, "brand_sub") and self.brand_sub.winfo_exists():
            self.brand_sub.configure(wraplength=int(max(250, w * 0.35)))

        if hasattr(self, "card") and self.card.winfo_exists():
            card_w = 0.8 if w > 1000 else 0.9
            card_h = 0.75 if h > 600 else 0.85
            self.card.place(relwidth=card_w, relheight=card_h, relx=0.5, rely=0.5, anchor="center")

    # ---------------------- AUTH LOGIC ----------------------
    def toggle_mode(self):
        self.is_signup = not self.is_signup
        if self.is_signup:
            self.title_label.configure(text="Join WorkTracker 🚀")
            self.subtitle_label.configure(text="Create your account below")
            # Unbind Enter during signup
            self.master.unbind("<Return>")
        else:
            self.title_label.configure(text="Welcome Back 👋")
            self.subtitle_label.configure(text="Sign in to continue to WorkTracker")
            # Rebind Enter during login
            self.bind_enter_key()
        self.build_login_fields()

    def bind_enter_key(self):
        """Bind Enter key only for login mode."""
        self.master.bind("<Return>", lambda event: self.handle_auth())

    def handle_auth(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        name = self.name_var.get().strip()

        if not username or not password or (self.is_signup and not name):
            messagebox.showwarning("Missing Info", "Please fill in all fields.")
            return

        if self.is_signup:
            success = auth.register_user(username, password)
            if success:
                messagebox.showinfo("Success", "Account created successfully!")
                self.toggle_mode()
            else:
                messagebox.showerror("Error", "Username already exists.")
        else:
            user = auth.authenticate_user(username, password)
            if user:
                # 🔹 Disable Enter key after login success
                self.master.unbind("<Return>")

                # Clear login UI
                for widget in self.master.winfo_children():
                    widget.destroy()
                open_dashboard(user, self.master)
            else:
                messagebox.showerror("Error", "Invalid username or password.")

