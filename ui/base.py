import tkinter as tk
from tkinter import ttk
from ui.theme import *

class BaseDashboard:
    """Shared layout: sidebar + main area, light theme."""

    NAV_ITEMS = []   # override: list of (emoji_label, method)
    ROLE_LABEL = ""

    def __init__(self, user, on_logout, title, geometry="1150x700"):
        self.user = user
        self.on_logout = on_logout
        self._current_nav = None

        self.root = tk.Tk()
        self.root.title(title)
        self.root.configure(bg=BG)
        self.root.geometry(geometry)
        self._center(geometry)
        self._build_shell()

    def _center(self, geometry):
        self.root.update_idletasks()
        w, h = map(int, geometry.split("x"))
        x = (self.root.winfo_screenwidth() - w) // 2
        y = (self.root.winfo_screenheight() - h) // 2
        self.root.geometry(f"{geometry}+{x}+{y}")

    def _build_shell(self):
        # Top accent strip
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x")

        container = tk.Frame(self.root, bg=BG)
        container.pack(fill="both", expand=True)

        # ── Sidebar ──────────────────────────────────────
        self.sidebar = tk.Frame(container, bg=SIDEBAR, width=210,
                                relief="solid", bd=0,
                                highlightthickness=1, highlightbackground=BORDER)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Logo
        logo = tk.Frame(self.sidebar, bg=SIDEBAR)
        logo.pack(fill="x", padx=20, pady=(20, 5))
        tk.Label(logo, text="📚 LearnPy", font=("Segoe UI", 13, "bold"),
                 bg=SIDEBAR, fg=ACCENT).pack(anchor="w")
        tk.Label(logo, text=self.ROLE_LABEL, font=("Segoe UI", 8, "bold"),
                 bg=SIDEBAR, fg=MUTED).pack(anchor="w")

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15, pady=12)

        # User chip
        chip = tk.Frame(self.sidebar, bg=ACCENT_LT, pady=8)
        chip.pack(fill="x", padx=12, pady=(0, 8))
        initials = "".join(p[0].upper() for p in self.user['full_name'].split()[:2])
        tk.Label(chip, text=initials, font=("Segoe UI", 11, "bold"),
                 bg=ACCENT, fg="white", width=3, pady=4).pack(side="left", padx=(8, 10))
        info = tk.Frame(chip, bg=ACCENT_LT)
        info.pack(side="left")
        tk.Label(info, text=self.user['full_name'][:20], font=("Segoe UI", 9, "bold"),
                 bg=ACCENT_LT, fg=TEXT).pack(anchor="w")
        tk.Label(info, text=self.user['role'].title(), font=("Segoe UI", 8),
                 bg=ACCENT_LT, fg=MUTED).pack(anchor="w")

        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15, pady=8)

        # Nav buttons
        self._nav_btn_refs = []
        for lbl, cmd in self.NAV_ITEMS:
            b = tk.Button(self.sidebar, text=lbl, command=lambda c=cmd, l=lbl: self._nav_click(c, l),
                          bg=SIDEBAR, fg=TEXT, font=("Segoe UI", 9), relief="flat",
                          cursor="hand2", bd=0, anchor="w", padx=18, pady=9,
                          activebackground=ACCENT_LT, activeforeground=ACCENT)
            b.pack(fill="x", padx=8)
            self._nav_btn_refs.append((lbl, b))

        # Logout at bottom
        tk.Frame(self.sidebar, bg=BORDER, height=1).pack(fill="x", padx=15, pady=8, side="bottom")
        tk.Button(self.sidebar, text="🚪  Sign Out", command=self._logout,
                  bg=SIDEBAR, fg=DANGER, font=("Segoe UI", 9), relief="flat",
                  cursor="hand2", bd=0, anchor="w", padx=18, pady=9,
                  activebackground=DANGER_LT, activeforeground=DANGER).pack(fill="x", padx=8, side="bottom")

        # ── Main area ─────────────────────────────────────
        self.main = tk.Frame(container, bg=BG)
        self.main.pack(side="left", fill="both", expand=True)

    def _nav_click(self, cmd, label):
        for lbl, b in self._nav_btn_refs:
            if lbl == label:
                b.config(bg=ACCENT_LT, fg=ACCENT, font=("Segoe UI", 9, "bold"))
            else:
                b.config(bg=SIDEBAR, fg=TEXT, font=("Segoe UI", 9))
        cmd()

    def clear_main(self):
        for w in self.main.winfo_children():
            w.destroy()

    def page_header(self, title, subtitle=""):
        hf = tk.Frame(self.main, bg=BG)
        hf.pack(fill="x", padx=25, pady=(22, 8))
        tk.Label(hf, text=title, font=("Segoe UI", 16, "bold"), bg=BG, fg=TEXT).pack(anchor="w")
        if subtitle:
            tk.Label(hf, text=subtitle, font=SMALL, bg=BG, fg=MUTED).pack(anchor="w", pady=(2, 0))
        tk.Frame(self.main, bg=BORDER, height=1).pack(fill="x", padx=25, pady=(0, 12))

    def _logout(self):
        self.root.destroy()
        self.on_logout()

    def run(self):
        self.root.mainloop()
