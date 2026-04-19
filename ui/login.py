import tkinter as tk
from tkinter import ttk
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from auth import login_user, register_user
from ui.theme import *

class AuthWindow:
    def __init__(self, on_login_success):
        self.on_login_success = on_login_success
        self.root = tk.Tk()
        self.root.title("LearnPy LMS")
        self.root.geometry("460x580")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self._center()
        self._build_login()
        self.root.mainloop()

    def _center(self):
        self.root.update_idletasks()
        w, h = 460, 580
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _build_login(self):
        self._clear()
        self.root.geometry("460x520")

        # Top accent bar
        tk.Frame(self.root, bg=ACCENT, height=4).pack(fill="x")

        outer = tk.Frame(self.root, bg=BG)
        outer.pack(expand=True, fill="both", padx=50, pady=30)

        # Logo area
        logo = tk.Frame(outer, bg=BG)
        logo.pack(pady=(10, 25))
        tk.Label(logo, text="📚", font=("Segoe UI", 32), bg=BG).pack()
        tk.Label(logo, text="LearnPy", font=("Segoe UI", 22, "bold"), bg=BG, fg=ACCENT).pack()
        tk.Label(logo, text="Learning Management System", font=SMALL, bg=BG, fg=MUTED).pack()

        # Card
        c = card_frame(outer)
        c.pack(fill="x", ipady=5)

        tk.Label(c, text="USERNAME", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(20, 4))
        self.u_entry = entry(c)
        self.u_entry.pack(fill="x", padx=25, ipady=6)

        tk.Label(c, text="PASSWORD", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(14, 4))
        self.p_entry = entry(c, show="•")
        self.p_entry.pack(fill="x", padx=25, ipady=6)

        self.msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        self.msg.pack(pady=(10, 0))

        login_btn = btn(c, "Sign In", self._do_login)
        login_btn.pack(fill="x", padx=25, pady=(8, 20))

        self.root.bind("<Return>", lambda e: self._do_login())

        # Footer
        f = tk.Frame(outer, bg=BG)
        f.pack(pady=15)
        tk.Label(f, text="Don't have an account? ", font=SMALL, bg=BG, fg=MUTED).pack(side="left")
        tk.Button(f, text="Register", font=("Segoe UI", 9, "bold"), bg=BG, fg=ACCENT,
                  relief="flat", cursor="hand2", bd=0,
                  command=self._build_register).pack(side="left")

    def _do_login(self):
        u = self.u_entry.get().strip()
        p = self.p_entry.get().strip()
        if not u or not p:
            self.msg.config(text="Please enter username and password.")
            return
        ok, result = login_user(u, p)
        if ok:
            self.root.destroy()
            self.on_login_success(result)
        else:
            self.msg.config(text="❌ " + result)

    def _build_register(self):
        self._clear()
        self.root.geometry("460,590")
        self.root.geometry("460x620")

        tk.Frame(self.root, bg=ACCENT, height=4).pack(fill="x")
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(expand=True, fill="both", padx=50, pady=20)

        tk.Label(outer, text="Create Account", font=TITLE, bg=BG, fg=TEXT).pack(anchor="w", pady=(10, 5))
        tk.Label(outer, text="Join LearnPy today", font=SMALL, bg=BG, fg=MUTED).pack(anchor="w", pady=(0, 15))

        c = card_frame(outer)
        c.pack(fill="x", ipady=5)

        self.reg = {}
        for lbl, hide in [("FULL NAME", False), ("USERNAME", False), ("PASSWORD", True)]:
            tk.Label(c, text=lbl, font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(14, 4))
            e = entry(c, show="•" if hide else None)
            e.pack(fill="x", padx=25, ipady=6)
            self.reg[lbl] = e

        tk.Label(c, text="ROLE", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(14, 4))
        self.role_var = tk.StringVar(value="student")
        rf = tk.Frame(c, bg=CARD)
        rf.pack(anchor="w", padx=25, pady=(0, 5))
        for val, lbl in [("student", "Student"), ("instructor", "Instructor")]:
            tk.Radiobutton(rf, text=lbl, variable=self.role_var, value=val,
                           bg=CARD, fg=TEXT, selectcolor=ACCENT, font=FONT,
                           activebackground=CARD).pack(side="left", padx=(0, 20))

        self.reg_msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        self.reg_msg.pack(pady=(8, 0))
        btn(c, "Create Account", self._do_register, color=SUCCESS).pack(fill="x", padx=25, pady=(8, 20))

        f = tk.Frame(outer, bg=BG)
        f.pack(pady=12)
        tk.Label(f, text="Already have an account? ", font=SMALL, bg=BG, fg=MUTED).pack(side="left")
        tk.Button(f, text="Sign In", font=("Segoe UI", 9, "bold"), bg=BG, fg=ACCENT,
                  relief="flat", cursor="hand2", bd=0, command=self._build_login).pack(side="left")

    def _do_register(self):
        name = self.reg["FULL NAME"].get().strip()
        uname = self.reg["USERNAME"].get().strip()
        pwd = self.reg["PASSWORD"].get().strip()
        role = self.role_var.get()
        if not name or not uname or not pwd:
            self.reg_msg.config(text="Please fill all fields.")
            return
        if len(pwd) < 4:
            self.reg_msg.config(text="Password must be at least 4 characters.")
            return
        ok, msg = register_user(uname, pwd, role, name)
        if ok:
            self.reg_msg.config(text="✓ Account created! Redirecting...", fg=SUCCESS)
            self.root.after(1000, self._build_login)
        else:
            self.reg_msg.config(text="❌ " + msg)
