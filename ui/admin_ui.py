import tkinter as tk
from tkinter import ttk, messagebox
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.base import BaseDashboard
from ui.theme import *
from database import (get_all_users, delete_user, get_platform_stats,
                      get_categories, add_category, delete_category)
from courses import get_all_courses, delete_course

class AdminDashboard(BaseDashboard):
    ROLE_LABEL = "ADMIN PANEL"
    NAV_ITEMS = []

    def __init__(self, user, on_logout):
        self.NAV_ITEMS = [
            ("📊   Dashboard",     self.show_dashboard),
            ("👥   Users",         self.show_users),
            ("📚   All Courses",   self.show_all_courses),
            ("🏷️   Categories",    self.show_categories),
        ]
        super().__init__(user, on_logout, "LearnPy — Admin Panel")
        self._nav_click(self.show_dashboard, "📊   Dashboard")
        self.run()

    # ── DASHBOARD ─────────────────────────────────────────
    def show_dashboard(self):
        self.clear_main()
        self.page_header("Platform Dashboard", "Overview of LearnPy statistics")

        stats = get_platform_stats()
        items = [
            ("👨‍🎓 Students",      stats['students'],    ACCENT,   ACCENT_LT),
            ("👨‍🏫 Instructors",   stats['instructors'], ACCENT2,  "#F5F0FF"),
            ("📚 Courses",        stats['courses'],     SUCCESS,  SUCCESS_LT),
            ("🎯 Enrollments",    stats['enrollments'], WARN,     WARN_LT),
            ("📝 Quiz Attempts",  stats['attempts'],    "#0891B2", "#E0F7FA"),
            ("📖 Lessons",        stats['lessons'],     MUTED,    BG),
        ]

        grid = tk.Frame(self.main, bg=BG)
        grid.pack(fill="x", padx=25, pady=10)

        for i, (label, value, color, bg_c) in enumerate(items):
            c = tk.Frame(grid, bg=bg_c, relief="solid", bd=1,
                         highlightthickness=1, highlightbackground=BORDER,
                         padx=25, pady=18)
            c.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="ew")
            grid.columnconfigure(i % 3, weight=1)
            tk.Label(c, text=str(value), font=("Segoe UI", 28, "bold"), bg=bg_c, fg=color).pack(anchor="w")
            tk.Label(c, text=label, font=("Segoe UI", 10), bg=bg_c, fg=MUTED).pack(anchor="w")

        # Recent users
        tk.Frame(self.main, bg=BORDER, height=1).pack(fill="x", padx=25, pady=15)
        tk.Label(self.main, text="RECENT USERS", font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=25, pady=(0, 8))

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)
        sf = scrollable(outer)

        users = get_all_users()[:10]
        for u in users:
            uf = tk.Frame(sf, bg=CARD, relief="solid", bd=1,
                          highlightthickness=1, highlightbackground=BORDER)
            uf.pack(fill="x", pady=3)
            row = tk.Frame(uf, bg=CARD)
            row.pack(fill="x", padx=15, pady=10)
            initials = "".join(p[0].upper() for p in u['full_name'].split()[:2])
            role_colors = {"student": (ACCENT, ACCENT_LT), "instructor": (ACCENT2, "#F5F0FF"), "admin": (DANGER, DANGER_LT)}
            rc, rb = role_colors.get(u['role'], (MUTED, BG))
            tk.Label(row, text=initials, font=("Segoe UI", 9, "bold"),
                     bg=rc, fg="white", width=3, pady=3).pack(side="left", padx=(0, 12))
            info = tk.Frame(row, bg=CARD)
            info.pack(side="left")
            tk.Label(info, text=u['full_name'], font=BOLD, bg=CARD, fg=TEXT).pack(anchor="w")
            tk.Label(info, text=f"@{u['username']}  •  Joined {str(u['created_at'])[:10]}",
                     font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w")
            tk.Label(row, text=f"  {u['role'].title()}  ",
                     font=("Segoe UI", 8, "bold"), bg=rb, fg=rc, pady=2).pack(side="right")

    # ── USERS ─────────────────────────────────────────────
    def show_users(self):
        self.clear_main()
        self.page_header("User Management", "View and manage all registered users")

        # Search
        sf_frame = tk.Frame(self.main, bg=BG)
        sf_frame.pack(fill="x", padx=25, pady=(0, 12))
        sbox = tk.Frame(sf_frame, bg=CARD, relief="solid", bd=1,
                        highlightthickness=1, highlightbackground=BORDER)
        sbox.pack(side="left")
        tk.Label(sbox, text="🔍", bg=CARD, fg=MUTED, font=FONT).pack(side="left", padx=(8, 4))
        self._user_sv = tk.StringVar()
        se = tk.Entry(sbox, textvariable=self._user_sv, bg=CARD, fg=TEXT,
                      relief="flat", font=FONT, width=25, insertbackground=ACCENT)
        se.pack(side="left", ipady=6, padx=(0, 8))

        # Role filter
        self._role_fv = tk.StringVar(value="All")
        rf = tk.Frame(sf_frame, bg=BG)
        rf.pack(side="left", padx=10)
        for role in ["All", "Student", "Instructor", "Admin"]:
            tk.Radiobutton(rf, text=role, variable=self._role_fv, value=role,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, font=SMALL,
                           command=lambda: refresh()).pack(side="left", padx=6)
        se.bind("<KeyRelease>", lambda e: refresh())

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)

        def refresh():
            for w in scroll_frame.winfo_children(): w.destroy()
            search = self._user_sv.get().strip().lower()
            role_f = self._role_fv.get()
            users = get_all_users()
            for u in users:
                if search and search not in u['full_name'].lower() and search not in u['username'].lower():
                    continue
                if role_f != "All" and u['role'] != role_f.lower():
                    continue
                self._user_row(scroll_frame, u, refresh)

        scroll_frame = scrollable(outer)
        refresh()

    def _user_row(self, parent, u, refresh_fn):
        uf = tk.Frame(parent, bg=CARD, relief="solid", bd=1,
                      highlightthickness=1, highlightbackground=BORDER)
        uf.pack(fill="x", pady=3)
        row = tk.Frame(uf, bg=CARD)
        row.pack(fill="x", padx=15, pady=10)

        initials = "".join(p[0].upper() for p in u['full_name'].split()[:2])
        role_colors = {"student": (ACCENT, ACCENT_LT), "instructor": (ACCENT2, "#F5F0FF"), "admin": (DANGER, DANGER_LT)}
        rc, rb = role_colors.get(u['role'], (MUTED, BG))
        tk.Label(row, text=initials, font=("Segoe UI", 9, "bold"),
                 bg=rc, fg="white", width=3, pady=3).pack(side="left", padx=(0, 12))

        info = tk.Frame(row, bg=CARD)
        info.pack(side="left")
        tk.Label(info, text=u['full_name'], font=BOLD, bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(info, text=f"@{u['username']}  •  Joined {str(u['created_at'])[:10]}",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w")

        tk.Label(row, text=f"  {u['role'].title()}  ",
                 font=("Segoe UI", 8, "bold"), bg=rb, fg=rc, pady=2).pack(side="right", padx=6)

        if u['role'] != 'admin':
            btn(row, "Delete", lambda uid=u['id'], name=u['full_name']: self._delete_user(uid, name, refresh_fn),
                color=DANGER, small=True).pack(side="right", padx=6)

    def _delete_user(self, user_id, name, refresh_fn):
        if messagebox.askyesno("Delete User", f"Delete user '{name}'? This cannot be undone."):
            delete_user(user_id)
            refresh_fn()

    # ── ALL COURSES ───────────────────────────────────────
    def show_all_courses(self):
        self.clear_main()
        self.page_header("All Courses", "View and manage every course on the platform")

        sf_frame = tk.Frame(self.main, bg=BG)
        sf_frame.pack(fill="x", padx=25, pady=(0, 12))
        sbox = tk.Frame(sf_frame, bg=CARD, relief="solid", bd=1,
                        highlightthickness=1, highlightbackground=BORDER)
        sbox.pack(side="left")
        tk.Label(sbox, text="🔍", bg=CARD, fg=MUTED, font=FONT).pack(side="left", padx=(8, 4))
        self._course_sv = tk.StringVar()
        se = tk.Entry(sbox, textvariable=self._course_sv, bg=CARD, fg=TEXT,
                      relief="flat", font=FONT, width=30, insertbackground=ACCENT)
        se.pack(side="left", ipady=6, padx=(0, 8))

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)

        def refresh():
            for w in sf.winfo_children(): w.destroy()
            search = self._course_sv.get().strip()
            courses = get_all_courses(search=search)
            if not courses:
                tk.Label(sf, text="No courses found.", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
                return
            for course in courses:
                self._course_row(sf, course, refresh)

        se.bind("<KeyRelease>", lambda e: refresh())
        sf = scrollable(outer)
        refresh()

    def _course_row(self, parent, course, refresh_fn):
        c = card_frame(parent)
        c.pack(fill="x", pady=4, ipady=3)
        top = tk.Frame(c, bg=CARD)
        top.pack(fill="x", padx=18, pady=(12, 4))
        if course.get('category_name'):
            tk.Label(top, text=f"  {course['category_name']}  ",
                     font=("Segoe UI", 8, "bold"), bg=ACCENT_LT, fg=ACCENT, pady=2).pack(side="right")
        tk.Label(top, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")
        tk.Label(c, text=f"By {course['instructor_name']}  •  Created {str(course['created_at'])[:10]}",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w", padx=18)
        bf = tk.Frame(c, bg=CARD)
        bf.pack(anchor="w", padx=18, pady=(6, 12))
        btn(bf, "🗑 Delete Course",
            lambda cid=course['id'], ct=course['title']: self._delete_course(cid, ct, refresh_fn),
            color=DANGER, small=True).pack(side="left")

    def _delete_course(self, course_id, title, refresh_fn):
        if messagebox.askyesno("Delete Course", f"Delete '{title}' and all its content?"):
            delete_course(course_id)
            refresh_fn()

    # ── CATEGORIES ────────────────────────────────────────
    def show_categories(self):
        self.clear_main()
        self.page_header("Category Management", "Add and remove course categories")

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)
        sf = scrollable(outer)

        # Add form
        af = card_frame(sf)
        af.pack(fill="x", pady=(0, 12), ipady=5)
        tk.Label(af, text="ADD NEW CATEGORY", font=("Segoe UI", 8, "bold"), bg=CARD, fg=ACCENT).pack(anchor="w", padx=18, pady=(14, 6))
        row = tk.Frame(af, bg=CARD)
        row.pack(anchor="w", padx=18, pady=(0, 14))
        cat_e = entry(row, width=30)
        cat_e.pack(side="left", ipady=6, padx=(0, 10))
        msg = tk.Label(row, text="", font=SMALL, bg=CARD, fg=DANGER)

        def add_cat():
            name = cat_e.get().strip()
            if not name:
                msg.config(text="Enter a category name.")
                return
            if add_category(name):
                cat_e.delete(0, "end")
                self.show_categories()
            else:
                msg.config(text="Category already exists.")

        btn(row, "+ Add", add_cat, color=SUCCESS, small=True).pack(side="left")
        msg.pack(side="left", padx=8)

        # Existing categories
        cats = get_categories()
        tk.Label(sf, text=f"EXISTING CATEGORIES  ({len(cats)})",
                 font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", pady=(8, 5))

        for cat in cats:
            cf = card_frame(sf)
            cf.pack(fill="x", pady=3)
            row = tk.Frame(cf, bg=CARD)
            row.pack(fill="x", padx=18, pady=12)
            tk.Label(row, text=f"🏷️  {cat['name']}", font=BOLD, bg=CARD, fg=TEXT).pack(side="left")
            btn(row, "Delete", lambda cid=cat['id'], cn=cat['name']: self._del_cat(cid, cn),
                color=DANGER, small=True).pack(side="right")

    def _del_cat(self, cat_id, name):
        if messagebox.askyesno("Delete Category", f"Delete category '{name}'?\nCourses in this category will become uncategorized."):
            delete_category(cat_id)
            self.show_categories()
