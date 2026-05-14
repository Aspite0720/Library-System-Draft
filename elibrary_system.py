import tkinter as tk
from tkinter import ttk, messagebox
from mysql.connector import Error
from datetime import datetime, timedelta
import hashlib

from db_config import get_connection
from db_setup import setup_database

# ══════════════════════════════════════════
#  COLORS / THEME
# ══════════════════════════════════════════
C = {
    "bg":      "#0F1923",
    "panel":   "#162231",
    "card":    "#1E2F42",
    "accent":  "#00C2A8",
    "accent2": "#0088CC",
    "danger":  "#E05252",
    "warn":    "#E0A852",
    "success": "#52C878",
    "text":    "#EAF0F6",
    "subtext": "#7A9BB5",
    "border":  "#2A3F55",
    "entry":   "#0F1923",
    "hover":   "#243650",
}

FONT_TITLE = ("Courier New", 18, "bold")
FONT_HEAD  = ("Courier New", 13, "bold")
FONT_SUBH  = ("Courier New", 11, "bold")
FONT_BODY  = ("Courier New", 10)
FONT_SMALL = ("Courier New", 9)
FONT_BTN   = ("Courier New", 10, "bold")

# ══════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def styled_btn(parent, text, cmd, color=None, width=18):
    bg = color or C["accent"]
    b = tk.Button(parent, text=text, command=cmd,
                  bg=bg, fg=C["bg"], font=FONT_BTN,
                  relief="flat", cursor="hand2",
                  activebackground=C["hover"], activeforeground=C["text"],
                  padx=10, pady=6, width=width)
    b.bind("<Enter>", lambda e: b.config(bg=C["hover"], fg=C["text"]))
    b.bind("<Leave>", lambda e: b.config(bg=bg, fg=C["bg"]))
    return b

def entry_field(parent, show=None, width=28):
    return tk.Entry(parent, font=FONT_BODY, bg=C["entry"], fg=C["text"],
                    insertbackground=C["accent"], relief="flat",
                    highlightbackground=C["border"], highlightcolor=C["accent"],
                    highlightthickness=1, width=width, show=show or "")

def make_table(parent, columns, col_widths=None):
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Custom.Treeview",
                    background=C["card"], foreground=C["text"],
                    fieldbackground=C["card"], rowheight=28, font=FONT_BODY)
    style.configure("Custom.Treeview.Heading",
                    background=C["panel"], foreground=C["accent"],
                    font=FONT_SUBH, relief="flat")
    style.map("Custom.Treeview", background=[("selected", C["accent2"])])

    frame = tk.Frame(parent, bg=C["bg"])
    sb = tk.Scrollbar(frame, orient="vertical")
    tree = ttk.Treeview(frame, columns=columns, show="headings",
                        yscrollcommand=sb.set, style="Custom.Treeview")
    sb.config(command=tree.yview)
    sb.pack(side="right", fill="y")
    tree.pack(side="left", fill="both", expand=True)

    for i, col in enumerate(columns):
        w = col_widths[i] if col_widths else 120
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="w")

    return frame, tree

# ══════════════════════════════════════════
#  LOGIN WINDOW
# ══════════════════════════════════════════

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("MCST E-Library Laptop Borrowing System")
        self.root.geometry("460x560")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        tk.Frame(self.root, bg=C["accent"], height=6).pack(fill="x")
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=40, pady=30)

        tk.Label(main, text="📚", font=("Courier New", 48),
                 bg=C["bg"], fg=C["accent"]).pack(pady=(10, 0))
        tk.Label(main, text="MCST E-Library", font=FONT_TITLE,
                 bg=C["bg"], fg=C["text"]).pack()
        tk.Label(main, text="Laptop Borrowing System", font=FONT_BODY,
                 bg=C["bg"], fg=C["subtext"]).pack(pady=(0, 25))

        card = tk.Frame(main, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x", pady=5)
        inner = tk.Frame(card, bg=C["panel"])
        inner.pack(padx=25, pady=25, fill="x")

        tk.Label(inner, text="Login As", font=FONT_SUBH,
                 bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
        self.role_var = tk.StringVar(value="Student")
        role_frame = tk.Frame(inner, bg=C["panel"])
        role_frame.pack(fill="x", pady=(5, 15))
        for role in ["Student", "Admin"]:
            tk.Radiobutton(role_frame, text=role, variable=self.role_var,
                           value=role, font=FONT_BODY,
                           bg=C["panel"], fg=C["text"],
                           selectcolor=C["card"],
                           activebackground=C["panel"],
                           activeforeground=C["accent"]).pack(side="left", padx=(0, 20))

        tk.Label(inner, text="Username", font=FONT_SUBH,
                 bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
        self.username_entry = entry_field(inner, width=32)
        self.username_entry.pack(fill="x", pady=(3, 12))

        tk.Label(inner, text="Password", font=FONT_SUBH,
                 bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
        self.password_entry = entry_field(inner, show="•", width=32)
        self.password_entry.pack(fill="x", pady=(3, 18))
        self.password_entry.bind("<Return>", lambda e: self._login())

        styled_btn(inner, "LOGIN", self._login, width=32).pack(fill="x")

        reg_frame = tk.Frame(main, bg=C["bg"])
        reg_frame.pack(pady=12)
        tk.Label(reg_frame, text="New student? ", font=FONT_SMALL,
                 bg=C["bg"], fg=C["subtext"]).pack(side="left")
        reg_lnk = tk.Label(reg_frame, text="Register here", font=FONT_SMALL,
                            bg=C["bg"], fg=C["accent"], cursor="hand2")
        reg_lnk.pack(side="left")
        reg_lnk.bind("<Button-1>", lambda e: self._open_register())

        tk.Label(main, text="Default admin: admin / admin123",
                 font=FONT_SMALL, bg=C["bg"], fg=C["border"]).pack()

    def _login(self):
        role   = self.role_var.get()
        uname  = self.username_entry.get().strip()
        passwd = self.password_entry.get().strip()
        if not uname or not passwd:
            messagebox.showwarning("Login", "Please fill in all fields.")
            return
        try:
            conn  = get_connection()
            cur   = conn.cursor(dictionary=True)
            table = "Admin" if role == "Admin" else "Student"
            cur.execute(f"SELECT * FROM {table} WHERE Username=%s AND Password=%s",
                        (uname, hash_pw(passwd)))
            user = cur.fetchone()
            cur.close(); conn.close()

            if user:
                self.root.withdraw()
                win = tk.Toplevel(self.root)
                win.protocol("WM_DELETE_WINDOW", lambda: self.root.destroy())
                if role == "Admin":
                    AdminDashboard(win, user, self.root)
                else:
                    StudentDashboard(win, user, self.root)
            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _open_register(self):
        win = tk.Toplevel(self.root)
        RegisterWindow(win)


# ══════════════════════════════════════════
#  REGISTER WINDOW
# ══════════════════════════════════════════

class RegisterWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Registration")
        self.root.geometry("420x540")
        self.root.configure(bg=C["bg"])
        self.root.resizable(False, False)
        self._build()

    def _build(self):
        tk.Frame(self.root, bg=C["accent"], height=5).pack(fill="x")
        main = tk.Frame(self.root, bg=C["bg"])
        main.pack(fill="both", expand=True, padx=35, pady=20)

        tk.Label(main, text="Student Registration", font=FONT_HEAD,
                 bg=C["bg"], fg=C["accent"]).pack(pady=(0, 15))

        card = tk.Frame(main, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=C["panel"])
        inner.pack(padx=20, pady=20, fill="x")

        fields = [
            ("Full Name",   "name"),
            ("Username",    "username"),
            ("Password",    "password"),
            ("Course",      "course"),
            ("Email",       "email"),
            ("Contact No.", "contact"),
        ]
        self.entries = {}
        for label, key in fields:
            tk.Label(inner, text=label, font=FONT_SMALL,
                     bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
            e = entry_field(inner, show="•" if key == "password" else None, width=32)
            e.pack(fill="x", pady=(2, 8))
            self.entries[key] = e

        styled_btn(inner, "REGISTER", self._register, width=32).pack(fill="x", pady=(5, 0))

    def _register(self):
        data = {k: e.get().strip() for k, e in self.entries.items()}
        if not data["name"] or not data["username"] or not data["password"]:
            messagebox.showwarning("Register", "Name, username, and password are required.")
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Student (Name, Username, Password, Course, Email, ContactNum)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data["name"], data["username"], hash_pw(data["password"]),
                  data["course"], data["email"], data["contact"]))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Success", "Account created! You may now log in.")
            self.root.destroy()
        except Error as e:
            if "Duplicate" in str(e):
                messagebox.showerror("Error", "Username already taken.")
            else:
                messagebox.showerror("DB Error", str(e))


# ══════════════════════════════════════════
#  STUDENT DASHBOARD
# ══════════════════════════════════════════

class StudentDashboard:
    def __init__(self, root, user, login_root):
        self.root       = root
        self.user       = user
        self.login_root = login_root
        self.root.title(f"Student Portal — {user['Name']}")
        self.root.geometry("900x620")
        self.root.configure(bg=C["bg"])
        self._build()

    def _build(self):
        sidebar = tk.Frame(self.root, bg=C["panel"], width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📚", font=("Courier New", 32),
                 bg=C["panel"], fg=C["accent"]).pack(pady=(20, 5))
        tk.Label(sidebar, text="E-Library", font=FONT_SUBH,
                 bg=C["panel"], fg=C["accent"]).pack()
        tk.Label(sidebar, text="Student Portal", font=FONT_SMALL,
                 bg=C["panel"], fg=C["subtext"]).pack(pady=(0, 20))
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x", padx=15)
        tk.Label(sidebar, text=f"👤 {self.user['Name']}", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"], wraplength=170).pack(pady=10)
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x", padx=15, pady=5)

        for label, cmd in [
            ("🖥  Borrow a Laptop", self._show_borrow),
            ("📋  My Requests",     self._show_my_requests),
            ("📜  My History",      self._show_history),
        ]:
            tk.Button(sidebar, text=label, font=FONT_BODY,
                      bg=C["panel"], fg=C["text"], relief="flat",
                      anchor="w", padx=15, pady=8, cursor="hand2",
                      activebackground=C["hover"],
                      command=cmd).pack(fill="x")

        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=15, side="bottom", pady=10)
        tk.Button(sidebar, text="⇠  Logout", font=FONT_BODY,
                  bg=C["panel"], fg=C["danger"], relief="flat",
                  anchor="w", padx=15, pady=8, cursor="hand2",
                  command=self._logout).pack(side="bottom", fill="x")

        self.main_area = tk.Frame(self.root, bg=C["bg"])
        self.main_area.pack(side="left", fill="both", expand=True)
        self._show_borrow()

    def _clear(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    # ── Borrow ──
    def _show_borrow(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Borrow a Laptop", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        styled_btn(top, "↻ Refresh", self._load_available,
                   color=C["accent2"], width=10).pack(side="right")

        cols = ["LaptopID", "Model", "Serial No.", "Status"]
        widths = [80, 200, 160, 100]
        tframe, self.avail_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_available()

        form = tk.Frame(main, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        form.pack(fill="x", padx=20, pady=(0, 15))
        inner = tk.Frame(form, bg=C["panel"])
        inner.pack(padx=15, pady=12, fill="x")

        tk.Label(inner, text="Select a laptop above, then set due date:",
                 font=FONT_SMALL, bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
        row = tk.Frame(inner, bg=C["panel"])
        row.pack(fill="x", pady=6)
        tk.Label(row, text="Due Date (YYYY-MM-DD):", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"]).pack(side="left")
        self.due_entry = entry_field(row, width=14)
        self.due_entry.insert(0, (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"))
        self.due_entry.pack(side="left", padx=8)
        styled_btn(row, "Submit Request", self._submit_borrow,
                   color=C["accent"], width=18).pack(side="left")

    def _load_available(self):
        for r in self.avail_tree.get_children():
            self.avail_tree.delete(r)
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT LaptopID, LaptopModel, SerialNo, Status FROM Laptop WHERE Status='Available'")
            for r in cur.fetchall():
                self.avail_tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _submit_borrow(self):
        sel = self.avail_tree.selection()
        if not sel:
            messagebox.showwarning("Borrow", "Please select a laptop.")
            return
        laptop_id = self.avail_tree.item(sel[0])["values"][0]
        try:
            due_date = datetime.strptime(self.due_entry.get().strip(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date. Use YYYY-MM-DD.")
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                INSERT INTO Borrow (StudentID, LaptopID, DueDate, Status)
                VALUES (%s, %s, %s, 'Pending')
            """, (self.user["StudentID"], laptop_id, due_date))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Success", "Borrow request submitted! Awaiting admin approval.")
            self._load_available()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── My Requests ──
    def _show_my_requests(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="My Borrow Requests", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        styled_btn(top, "↻ Refresh", self._show_my_requests,
                   color=C["accent2"], width=10).pack(side="right")

        cols = ["BorrowID", "Laptop Model", "Serial No.", "Due Date", "Status", "Notes"]
        widths = [80, 180, 130, 120, 100, 150]
        tframe, tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, l.LaptopModel, l.SerialNo,
                       DATE(b.DueDate), b.Status, IFNULL(b.Notes,'')
                FROM Borrow b
                JOIN Laptop l ON b.LaptopID=l.LaptopID
                WHERE b.StudentID=%s
                ORDER BY b.BorrowID DESC
            """, (self.user["StudentID"],))
            for r in cur.fetchall():
                tag = "od" if r[4]=="Overdue" else ("ok" if r[4]=="Approved" else "normal")
                tree.insert("", "end", values=r, tags=(tag,))
            tree.tag_configure("od", foreground=C["danger"])
            tree.tag_configure("ok", foreground=C["success"])
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── My History ──
    def _show_history(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(main, text="My Borrowing History", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=20, pady=15)

        cols = ["BorrowID", "Laptop", "Borrow Date", "Due Date", "Return Date", "Status"]
        widths = [80, 180, 120, 120, 120, 100]
        tframe, tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, l.LaptopModel,
                       IFNULL(DATE(b.BorrowDate),'—'),
                       IFNULL(DATE(b.DueDate),'—'),
                       IFNULL(DATE(b.ReturnDate),'—'),
                       b.Status
                FROM Borrow b
                JOIN Laptop l ON b.LaptopID=l.LaptopID
                WHERE b.StudentID=%s
                ORDER BY b.BorrowID DESC
            """, (self.user["StudentID"],))
            for r in cur.fetchall():
                tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _logout(self):
        self.root.destroy()
        self.login_root.deiconify()


# ══════════════════════════════════════════
#  ADMIN DASHBOARD
# ══════════════════════════════════════════

class AdminDashboard:
    def __init__(self, root, user, login_root):
        self.root       = root
        self.user       = user
        self.login_root = login_root
        self.root.title(f"Admin Dashboard — {user['Name']}")
        self.root.geometry("1100x680")
        self.root.configure(bg=C["bg"])
        self._build()

    def _build(self):
        sidebar = tk.Frame(self.root, bg=C["panel"], width=210)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📚", font=("Courier New", 32),
                 bg=C["panel"], fg=C["accent"]).pack(pady=(20, 5))
        tk.Label(sidebar, text="E-Library", font=FONT_SUBH,
                 bg=C["panel"], fg=C["accent"]).pack()
        tk.Label(sidebar, text="Admin Dashboard", font=FONT_SMALL,
                 bg=C["panel"], fg=C["subtext"]).pack(pady=(0, 10))
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x", padx=15)
        tk.Label(sidebar, text=f"🔑 {self.user['Name']}", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"], wraplength=180).pack(pady=8)
        tk.Frame(sidebar, bg=C["border"], height=1).pack(fill="x", padx=15, pady=5)

        for label, cmd in [
            ("📊  Dashboard",        self._show_dashboard),
            ("✅  Pending Requests", self._show_pending),
            ("📋  All Transactions", self._show_transactions),
            ("🖥  Laptop Inventory", self._show_inventory),
            ("👥  Manage Students",  self._show_students),
            ("📈  Reports",          self._show_reports),
        ]:
            tk.Button(sidebar, text=label, font=FONT_BODY,
                      bg=C["panel"], fg=C["text"], relief="flat",
                      anchor="w", padx=15, pady=8, cursor="hand2",
                      activebackground=C["hover"],
                      command=cmd).pack(fill="x")

        tk.Frame(sidebar, bg=C["border"], height=1).pack(
            fill="x", padx=15, side="bottom", pady=10)
        tk.Button(sidebar, text="⇠  Logout", font=FONT_BODY,
                  bg=C["panel"], fg=C["danger"], relief="flat",
                  anchor="w", padx=15, pady=8, cursor="hand2",
                  command=self._logout).pack(side="bottom", fill="x")

        self.main_area = tk.Frame(self.root, bg=C["bg"])
        self.main_area.pack(side="left", fill="both", expand=True)
        self._show_dashboard()

    def _clear(self):
        for w in self.main_area.winfo_children():
            w.destroy()

    # ── Dashboard ──
    def _show_dashboard(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(main, text="Dashboard Overview", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=20, pady=15)

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM Laptop WHERE Status='Available'"); avail    = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Laptop WHERE Status='Borrowed'");  borrowed = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Pending'");   pending  = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Student WHERE Status='active'");   students = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Borrow WHERE Status='Approved' AND DueDate < NOW()"); overdue = cur.fetchone()[0]
            cur.execute("UPDATE Borrow SET Status='Overdue' WHERE Status='Approved' AND DueDate < NOW()")
            conn.commit()
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e)); return

        cards_row = tk.Frame(main, bg=C["bg"])
        cards_row.pack(fill="x", padx=20, pady=5)
        for title, val, color in [
            ("Available Laptops", avail,    C["success"]),
            ("Borrowed",          borrowed,  C["accent2"]),
            ("Pending Requests",  pending,   C["warn"]),
            ("Active Students",   students,  C["accent"]),
            ("Overdue",           overdue,   C["danger"]),
        ]:
            card = tk.Frame(cards_row, bg=C["card"],
                            highlightbackground=color, highlightthickness=2)
            card.pack(side="left", fill="both", expand=True, padx=5)
            tk.Frame(card, bg=color, height=4).pack(fill="x")
            tk.Label(card, text=str(val), font=("Courier New", 28, "bold"),
                     bg=C["card"], fg=color).pack(pady=(10, 0))
            tk.Label(card, text=title, font=FONT_SMALL,
                     bg=C["card"], fg=C["subtext"]).pack(pady=(0, 10))

        tk.Label(main, text="Recent Transactions", font=FONT_SUBH,
                 bg=C["bg"], fg=C["subtext"]).pack(anchor="w", padx=20, pady=(20, 5))
        cols = ["BorrowID", "Student", "Laptop", "Borrow Date", "Due Date", "Status"]
        widths = [80, 160, 160, 120, 120, 100]
        tframe, tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, s.Name, l.LaptopModel,
                       IFNULL(DATE(b.BorrowDate),'—'),
                       IFNULL(DATE(b.DueDate),'—'), b.Status
                FROM Borrow b
                JOIN Student s ON b.StudentID=s.StudentID
                JOIN Laptop  l ON b.LaptopID=l.LaptopID
                ORDER BY b.BorrowID DESC LIMIT 20
            """)
            for r in cur.fetchall():
                tag = "od" if r[5]=="Overdue" else ("pend" if r[5]=="Pending" else "normal")
                tree.insert("", "end", values=r, tags=(tag,))
            tree.tag_configure("od",   foreground=C["danger"])
            tree.tag_configure("pend", foreground=C["warn"])
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── Pending Requests ──
    def _show_pending(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["warn"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Pending Borrow Requests", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        styled_btn(top, "↻ Refresh", self._show_pending,
                   color=C["accent2"], width=10).pack(side="right")

        cols = ["BorrowID", "Student", "Laptop", "Serial No.", "Due Date", "Requested"]
        widths = [80, 160, 160, 130, 110, 110]
        tframe, self.pend_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_pending()

        btn_frame = tk.Frame(main, bg=C["bg"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 8))
        styled_btn(btn_frame, "✔ Approve", self._approve,
                   color=C["success"], width=14).pack(side="left", padx=(0, 10))
        styled_btn(btn_frame, "✘ Reject",  self._reject,
                   color=C["danger"],  width=14).pack(side="left")

        notes_frame = tk.Frame(main, bg=C["panel"],
                               highlightbackground=C["border"], highlightthickness=1)
        notes_frame.pack(fill="x", padx=20, pady=(0, 15))
        inner = tk.Frame(notes_frame, bg=C["panel"])
        inner.pack(padx=12, pady=10, fill="x")
        tk.Label(inner, text="Rejection Notes (optional):", font=FONT_SMALL,
                 bg=C["panel"], fg=C["subtext"]).pack(anchor="w")
        self.notes_entry = entry_field(inner, width=60)
        self.notes_entry.pack(fill="x", pady=(3, 0))

    def _load_pending(self):
        for r in self.pend_tree.get_children():
            self.pend_tree.delete(r)
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, s.Name, l.LaptopModel, l.SerialNo,
                       DATE(b.DueDate), IFNULL(DATE(b.BorrowDate),'—')
                FROM Borrow b
                JOIN Student s ON b.StudentID=s.StudentID
                JOIN Laptop  l ON b.LaptopID=l.LaptopID
                WHERE b.Status='Pending' ORDER BY b.BorrowID
            """)
            for r in cur.fetchall():
                self.pend_tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _approve(self):
        sel = self.pend_tree.selection()
        if not sel:
            messagebox.showwarning("Approve", "Select a request first."); return
        borrow_id = self.pend_tree.item(sel[0])["values"][0]
        serial_no = self.pend_tree.item(sel[0])["values"][3]
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT LaptopID FROM Laptop WHERE SerialNo=%s", (serial_no,))
            lid = cur.fetchone()[0]
            cur.execute("""
                UPDATE Borrow SET Status='Approved', AdminID=%s, BorrowDate=NOW()
                WHERE BorrowID=%s
            """, (self.user["AdminID"], borrow_id))
            cur.execute("UPDATE Laptop SET Status='Borrowed' WHERE LaptopID=%s", (lid,))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Approved", f"Request #{borrow_id} approved.")
            self._load_pending()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _reject(self):
        sel = self.pend_tree.selection()
        if not sel:
            messagebox.showwarning("Reject", "Select a request first."); return
        borrow_id = self.pend_tree.item(sel[0])["values"][0]
        notes     = self.notes_entry.get().strip()
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                UPDATE Borrow SET Status='Rejected', AdminID=%s, Notes=%s
                WHERE BorrowID=%s
            """, (self.user["AdminID"], notes, borrow_id))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Rejected", f"Request #{borrow_id} rejected.")
            self._load_pending()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── All Transactions ──
    def _show_transactions(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent2"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="All Transactions", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")
        styled_btn(top, "↻ Refresh", self._show_transactions,
                   color=C["accent2"], width=10).pack(side="right")

        cols = ["BorrowID", "Student", "Laptop", "Borrow Date", "Due Date", "Return Date", "Status"]
        widths = [75, 150, 150, 110, 110, 110, 90]
        tframe, self.trans_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_transactions()

        btn_frame = tk.Frame(main, bg=C["bg"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        styled_btn(btn_frame, "Mark as Returned", self._mark_returned,
                   color=C["success"], width=18).pack(side="left")

    def _load_transactions(self):
        for r in self.trans_tree.get_children():
            self.trans_tree.delete(r)
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, s.Name, l.LaptopModel,
                       IFNULL(DATE(b.BorrowDate),'—'),
                       IFNULL(DATE(b.DueDate),'—'),
                       IFNULL(DATE(b.ReturnDate),'—'),
                       b.Status
                FROM Borrow b
                JOIN Student s ON b.StudentID=s.StudentID
                JOIN Laptop  l ON b.LaptopID=l.LaptopID
                ORDER BY b.BorrowID DESC
            """)
            for r in cur.fetchall():
                tag = "od" if r[6]=="Overdue" else "normal"
                self.trans_tree.insert("", "end", values=r, tags=(tag,))
            self.trans_tree.tag_configure("od", foreground=C["danger"])
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _mark_returned(self):
        sel = self.trans_tree.selection()
        if not sel:
            messagebox.showwarning("Return", "Select a transaction."); return
        row = self.trans_tree.item(sel[0])["values"]
        borrow_id = row[0]
        if row[6] not in ("Approved", "Overdue"):
            messagebox.showwarning("Return", "Only Approved/Overdue items can be returned."); return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT LaptopID FROM Borrow WHERE BorrowID=%s", (borrow_id,))
            lid = cur.fetchone()[0]
            cur.execute("UPDATE Borrow SET Status='Returned', ReturnDate=NOW() WHERE BorrowID=%s", (borrow_id,))
            cur.execute("UPDATE Laptop SET Status='Available' WHERE LaptopID=%s", (lid,))
            conn.commit()
            cur.close(); conn.close()
            messagebox.showinfo("Returned", f"Transaction #{borrow_id} marked as Returned.")
            self._load_transactions()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── Inventory ──
    def _show_inventory(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Laptop Inventory", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")

        cols = ["LaptopID", "Model", "Serial No.", "Status"]
        widths = [80, 220, 180, 120]
        tframe, self.inv_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_inventory()

        form = tk.Frame(main, bg=C["panel"],
                        highlightbackground=C["border"], highlightthickness=1)
        form.pack(fill="x", padx=20, pady=(0, 15))
        inner = tk.Frame(form, bg=C["panel"])
        inner.pack(padx=15, pady=12, fill="x")

        row1 = tk.Frame(inner, bg=C["panel"])
        row1.pack(fill="x", pady=4)
        tk.Label(row1, text="Model:", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"]).pack(side="left")
        self.inv_model = entry_field(row1, width=20)
        self.inv_model.pack(side="left", padx=8)
        tk.Label(row1, text="Serial No.:", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"]).pack(side="left")
        self.inv_serial = entry_field(row1, width=16)
        self.inv_serial.pack(side="left", padx=8)

        row2 = tk.Frame(inner, bg=C["panel"])
        row2.pack(fill="x", pady=4)
        tk.Label(row2, text="Status:", font=FONT_SMALL,
                 bg=C["panel"], fg=C["text"]).pack(side="left")
        self.inv_status = ttk.Combobox(row2,
            values=["Available", "Under Repair", "Lost"],
            font=FONT_BODY, width=14, state="readonly")
        self.inv_status.set("Available")
        self.inv_status.pack(side="left", padx=8)
        styled_btn(row2, "Add Laptop",    self._add_laptop,           color=C["success"], width=12).pack(side="left", padx=4)
        styled_btn(row2, "Update Status", self._update_laptop_status, color=C["warn"],    width=14).pack(side="left", padx=4)
        styled_btn(row2, "Delete",        self._delete_laptop,        color=C["danger"],  width=10).pack(side="left", padx=4)

    def _load_inventory(self):
        for r in self.inv_tree.get_children():
            self.inv_tree.delete(r)
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT LaptopID, LaptopModel, SerialNo, Status FROM Laptop ORDER BY LaptopID")
            for r in cur.fetchall():
                tag = {"Available": "avail", "Borrowed": "borrow"}.get(r[3], "repair")
                self.inv_tree.insert("", "end", values=r, tags=(tag,))
            self.inv_tree.tag_configure("avail",  foreground=C["success"])
            self.inv_tree.tag_configure("borrow", foreground=C["accent2"])
            self.inv_tree.tag_configure("repair", foreground=C["warn"])
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _add_laptop(self):
        model  = self.inv_model.get().strip()
        serial = self.inv_serial.get().strip()
        if not model or not serial:
            messagebox.showwarning("Add", "Model and Serial No. are required."); return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("INSERT INTO Laptop (LaptopModel, SerialNo, Status, AdminID) VALUES (%s,%s,'Available',%s)",
                        (model, serial, self.user["AdminID"]))
            conn.commit()
            cur.close(); conn.close()
            self._load_inventory()
            self.inv_model.delete(0, "end")
            self.inv_serial.delete(0, "end")
        except Error as e:
            if "Duplicate" in str(e):
                messagebox.showerror("Error", "Serial number already exists.")
            else:
                messagebox.showerror("DB Error", str(e))

    def _update_laptop_status(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showwarning("Update", "Select a laptop first."); return
        lid = self.inv_tree.item(sel[0])["values"][0]
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("UPDATE Laptop SET Status=%s WHERE LaptopID=%s", (self.inv_status.get(), lid))
            conn.commit()
            cur.close(); conn.close()
            self._load_inventory()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _delete_laptop(self):
        sel = self.inv_tree.selection()
        if not sel:
            messagebox.showwarning("Delete", "Select a laptop first."); return
        lid = self.inv_tree.item(sel[0])["values"][0]
        if not messagebox.askyesno("Confirm", f"Delete Laptop ID {lid}? This cannot be undone."):
            return
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("DELETE FROM Borrow WHERE LaptopID=%s", (lid,))
            cur.execute("DELETE FROM Laptop WHERE LaptopID=%s", (lid,))
            conn.commit()
            cur.close(); conn.close()
            self._load_inventory()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── Students ──
    def _show_students(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        top = tk.Frame(main, bg=C["bg"])
        top.pack(fill="x", padx=20, pady=15)
        tk.Label(top, text="Manage Students", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(side="left")

        cols = ["StudentID", "Name", "Username", "Course", "Email", "Contact", "Status"]
        widths = [80, 150, 110, 130, 160, 110, 80]
        tframe, self.stu_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._load_students()

        btn_frame = tk.Frame(main, bg=C["bg"])
        btn_frame.pack(fill="x", padx=20, pady=(0, 15))
        styled_btn(btn_frame, "Toggle Active/Inactive", self._toggle_student,
                   color=C["warn"], width=22).pack(side="left", padx=(0, 10))
        styled_btn(btn_frame, "View History", self._view_student_history,
                   color=C["accent2"], width=14).pack(side="left")

    def _load_students(self):
        for r in self.stu_tree.get_children():
            self.stu_tree.delete(r)
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT StudentID, Name, Username, IFNULL(Course,''), IFNULL(Email,''),
                       IFNULL(ContactNum,''), Status
                FROM Student ORDER BY StudentID
            """)
            for r in cur.fetchall():
                self.stu_tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _toggle_student(self):
        sel = self.stu_tree.selection()
        if not sel:
            messagebox.showwarning("Student", "Select a student."); return
        row = self.stu_tree.item(sel[0])["values"]
        new_status = "inactive" if row[6] == "active" else "active"
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("UPDATE Student SET Status=%s WHERE StudentID=%s", (new_status, row[0]))
            conn.commit()
            cur.close(); conn.close()
            self._load_students()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _view_student_history(self):
        sel = self.stu_tree.selection()
        if not sel:
            messagebox.showwarning("History", "Select a student."); return
        row = self.stu_tree.item(sel[0])["values"]
        sid, sname = row[0], row[1]

        win = tk.Toplevel(self.root)
        win.title(f"History — {sname}")
        win.geometry("700x400")
        win.configure(bg=C["bg"])
        tk.Label(win, text=f"History: {sname}", font=FONT_HEAD,
                 bg=C["bg"], fg=C["accent"]).pack(pady=10)

        cols = ["BorrowID", "Laptop", "Borrow Date", "Due Date", "Return Date", "Status"]
        widths = [80, 180, 110, 110, 110, 90]
        tframe, tree = make_table(win, cols, widths)
        tframe.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, l.LaptopModel,
                       IFNULL(DATE(b.BorrowDate),'—'),
                       IFNULL(DATE(b.DueDate),'—'),
                       IFNULL(DATE(b.ReturnDate),'—'),
                       b.Status
                FROM Borrow b
                JOIN Laptop l ON b.LaptopID=l.LaptopID
                WHERE b.StudentID=%s ORDER BY b.BorrowID DESC
            """, (sid,))
            for r in cur.fetchall():
                tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    # ── Reports ──
    def _show_reports(self):
        self._clear()
        main = self.main_area
        tk.Frame(main, bg=C["accent"], height=3).pack(fill="x")
        tk.Label(main, text="Reports", font=FONT_HEAD,
                 bg=C["bg"], fg=C["text"]).pack(anchor="w", padx=20, pady=15)

        btn_row = tk.Frame(main, bg=C["bg"])
        btn_row.pack(fill="x", padx=20, pady=(0, 10))
        for label, cmd in [
            ("Overdue Laptops",     self._rpt_overdue),
            ("Inventory Status",    self._rpt_inventory),
            ("Borrowing Frequency", self._rpt_frequency),
        ]:
            styled_btn(btn_row, label, cmd, width=20).pack(side="left", padx=(0, 10))

        cols = ["Col1", "Col2", "Col3", "Col4", "Col5"]
        widths = [80, 200, 160, 130, 130]
        tframe, self.rpt_tree = make_table(main, cols, widths)
        tframe.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        self._rpt_overdue()

    def _set_rpt_cols(self, cols, widths):
        self.rpt_tree["columns"] = cols
        for col, w in zip(cols, widths):
            self.rpt_tree.heading(col, text=col)
            self.rpt_tree.column(col, width=w, anchor="w")
        for r in self.rpt_tree.get_children():
            self.rpt_tree.delete(r)

    def _rpt_overdue(self):
        self._set_rpt_cols(
            ["BorrowID", "Student", "Laptop", "Due Date", "Days Overdue"],
            [80, 160, 160, 120, 110])
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT b.BorrowID, s.Name, l.LaptopModel,
                       DATE(b.DueDate), DATEDIFF(NOW(), b.DueDate)
                FROM Borrow b
                JOIN Student s ON b.StudentID=s.StudentID
                JOIN Laptop  l ON b.LaptopID=l.LaptopID
                WHERE b.Status='Overdue' ORDER BY b.DueDate
            """)
            for r in cur.fetchall():
                self.rpt_tree.insert("", "end", values=r, tags=("od",))
            self.rpt_tree.tag_configure("od", foreground=C["danger"])
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _rpt_inventory(self):
        self._set_rpt_cols(
            ["LaptopID", "Model", "Serial No.", "Status"],
            [80, 220, 180, 120])
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("SELECT LaptopID, LaptopModel, SerialNo, Status FROM Laptop ORDER BY Status")
            for r in cur.fetchall():
                self.rpt_tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _rpt_frequency(self):
        self._set_rpt_cols(
            ["Student", "Total Borrows", "Returned", "Overdue"],
            [200, 140, 120, 120])
        try:
            conn = get_connection()
            cur  = conn.cursor()
            cur.execute("""
                SELECT s.Name,
                       COUNT(*) AS total,
                       SUM(b.Status='Returned') AS returned,
                       SUM(b.Status='Overdue')  AS overdue
                FROM Borrow b
                JOIN Student s ON b.StudentID=s.StudentID
                GROUP BY s.StudentID ORDER BY total DESC
            """)
            for r in cur.fetchall():
                self.rpt_tree.insert("", "end", values=r)
            cur.close(); conn.close()
        except Error as e:
            messagebox.showerror("DB Error", str(e))

    def _logout(self):
        self.root.destroy()
        self.login_root.deiconify()


# ══════════════════════════════════════════
#  MAIN ENTRY POINT
# ══════════════════════════════════════════

if __name__ == "__main__":
    setup_database()        # creates DB + tables (from db_setup.py)
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
