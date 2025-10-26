import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import db


def open_analytics(username, root):
    """Open the full analytics dashboard window."""
    win = ttk.Toplevel(root)
    win.title("Analytics Dashboard")
    win.geometry("950x650")
    win.resizable(False, False)

    ttk.Label(win, text=f"Analytics Dashboard - {username}",
              font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=20, pady=(10, 5))

    ttk.Label(win, text="Analyze task completion trends, categories, and productivity insights.",
              font=("Segoe UI", 10), foreground="#6c757d").pack(anchor="w", padx=20, pady=(0, 10))

    # --- Filter frame ---
    filter_frame = ttk.Frame(win)
    filter_frame.pack(fill="x", padx=20, pady=10)

    ttk.Label(filter_frame, text="Start Date:").pack(side="left", padx=(0, 5))
    start_entry = DateEntry(filter_frame, dateformat="%Y-%m-%d")
    start_entry.pack(side="left", padx=(0, 15))

    ttk.Label(filter_frame, text="End Date:").pack(side="left", padx=(0, 5))
    end_entry = DateEntry(filter_frame, dateformat="%Y-%m-%d")
    end_entry.pack(side="left", padx=(0, 15))

    ttk.Button(filter_frame, text="Apply Filter", bootstyle="info-outline",
               command=lambda: load_data()).pack(side="left")

    # --- Table frame ---
    table_frame = ttk.Frame(win)
    table_frame.pack(fill="both", expand=True, padx=20, pady=10)

    table = Tableview(
        master=table_frame,
        coldata=["Task Name", "Category", "Status", "Start", "Due"],
        rowdata=[],
        paginated=False,
        searchable=True,
        bootstyle="info",
        autofit=True,
        stripecolor=("white", "#f8f9fa")
    )
    table.pack(fill="both", expand=True)

    # --- Chart frame ---
    chart_frame = ttk.Frame(win)
    chart_frame.pack(fill="x", padx=20, pady=(0, 15))

    chart_canvas = None

    def load_data():
        nonlocal chart_canvas
        table.delete_rows()  # ✅ fixed: clear existing rows properly

        conn = db.connect()
        cursor = conn.cursor()
        query = "SELECT title, category, status, start_date, due_date FROM tasks WHERE username=?"
        cursor.execute(query, (username,))
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            Messagebox.show_info("No data to display.")
            return

        df = pd.DataFrame(rows, columns=["Task Name", "Category", "Status", "Start", "Due"])

        # ✅ Convert to datetime safely
        for col in ["Start", "Due"]:
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # Apply date filters
        try:
            s_date = datetime.strptime(start_entry.entry.get(), "%Y-%m-%d") if start_entry.entry.get() else None
            e_date = datetime.strptime(end_entry.entry.get(), "%Y-%m-%d") if end_entry.entry.get() else None
        except ValueError:
            Messagebox.show_error("Invalid date format.")
            return

        if s_date is not None:
            df = df[df["Start"] >= s_date]
        if e_date is not None:
            df = df[df["Due"] <= e_date]

        # ✅ Add filtered data to table
        for row in df.values.tolist():
            table.insert_row(row)

        # --- Chart section ---
        if chart_canvas:
            chart_canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(7.5, 3.5), dpi=100)
        ax = fig.add_subplot(111)

        status_counts = df["Status"].value_counts()
        ax.bar(status_counts.index, status_counts.values)
        ax.set_title("Task Distribution by Status", fontsize=10)
        ax.set_ylabel("Count")

        chart_canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        chart_canvas.draw()
        chart_canvas.get_tk_widget().pack(fill="x", expand=True)

    # Initial data load
    load_data()


# ---------- Helper Functions ----------
def build_tasks_dataframe(rows):
    """
    Convert task rows to a clean pandas DataFrame.
    Accepts either the older (title, start, due, status) rows or the full rows.
    """
    if not rows:
        return pd.DataFrame(columns=["Title", "Start", "Due", "Status"])

    first = rows[0]
    if len(first) == 4:
        df = pd.DataFrame(rows, columns=["Title", "Start", "Due", "Status"])
    else:
        df = pd.DataFrame(rows, columns=[
            "ID", "UserID", "Username", "Title", "Start", "Due",
            "Status", "Description", "Priority", "Category", "EstimatedMinutes"
        ])
        df = df.rename(columns={"Title": "Title", "Start": "Start", "Due": "Due", "Status": "Status"})

    # ✅ Convert date columns safely
    for col in ["Start", "Due"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def compute_stats(df):
    """Compute overall task statistics safely."""
    stats = {
        "total": len(df),
        "completed": int((df["Status"].astype(str).str.lower() == "completed").sum()) if "Status" in df.columns else 0,
        "in_progress": int((df["Status"].astype(str).str.lower() == "in progress").sum()) if "Status" in df.columns else 0,
        "overdue": int((df["Status"].astype(str).str.lower() == "overdue").sum()) if "Status" in df.columns else 0
    }

    # ✅ Compute monthly counts safely
    if "Start" in df.columns:
        try:
            df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
            if df["Start"].notna().any():
                stats["monthly_counts"] = df.groupby(df["Start"].dt.to_period("M")).size()
            else:
                stats["monthly_counts"] = pd.Series([], dtype=int)
        except Exception:
            stats["monthly_counts"] = pd.Series([], dtype=int)
    else:
        stats["monthly_counts"] = pd.Series([], dtype=int)

    return stats
