import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.base import BaseDashboard
from ui.theme import *
from courses import (create_course, get_instructor_courses, update_course,
                     delete_course, add_lesson, get_lessons, delete_lesson)
from quiz import create_quiz, add_question, get_quizzes, get_questions, delete_quiz
from database import get_categories, update_profile, get_user, change_password

class InstructorDashboard(BaseDashboard):
    ROLE_LABEL = "INSTRUCTOR PORTAL"
    NAV_ITEMS = []  # built in __init__

    def __init__(self, user, on_logout):
        self.NAV_ITEMS = [
            ("📚   My Courses",    self.show_courses),
            ("➕   New Course",    self.show_new_course),
            ("📝   Quiz Manager",  self.show_quizzes),
            ("👤   My Profile",   self.show_profile),
        ]
        super().__init__(user, on_logout, f"LearnPy — Instructor Dashboard")
        self._nav_click(self.show_courses, "📚   My Courses")
        self.run()

    # ── Search bar helper ─────────────────────────────────
    def _search_bar(self, parent, on_search, categories):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=25, pady=(0, 12))

        # Search entry
        sf = tk.Frame(f, bg=CARD, relief="solid", bd=1,
                      highlightthickness=1, highlightbackground=BORDER)
        sf.pack(side="left", padx=(0, 10))
        tk.Label(sf, text="🔍", bg=CARD, fg=MUTED, font=FONT).pack(side="left", padx=(8, 4))
        self._search_var = tk.StringVar()
        se = tk.Entry(sf, textvariable=self._search_var, bg=CARD, fg=TEXT,
                      relief="flat", font=FONT, width=22, insertbackground=ACCENT)
        se.pack(side="left", ipady=6, padx=(0, 8))
        se.bind("<KeyRelease>", lambda e: on_search())

        # Category dropdown
        self._cat_var = tk.StringVar(value="All Categories")
        cat_names = ["All Categories"] + [c['name'] for c in categories]
        self._cat_map = {c['name']: c['id'] for c in categories}
        dd = ttk.Combobox(f, textvariable=self._cat_var, values=cat_names,
                          state="readonly", font=FONT, width=18)
        dd.pack(side="left")
        dd.bind("<<ComboboxSelected>>", lambda e: on_search())
        return self._search_var, self._cat_var

    def _get_filter(self):
        search = getattr(self, '_search_var', None)
        cat_var = getattr(self, '_cat_var', None)
        s = search.get().strip() if search else ""
        cat_name = cat_var.get() if cat_var else "All Categories"
        cat_id = self._cat_map.get(cat_name) if hasattr(self, '_cat_map') else None
        return s, cat_id

    # ── COURSES ───────────────────────────────────────────
    def show_courses(self):
        self.clear_main()
        self.page_header("My Courses", "Manage your courses and lessons")
        cats = get_categories()

        def refresh():
            for w in scroll_frame.winfo_children():
                w.destroy()
            s, cid = self._get_filter()
            courses = get_instructor_courses(self.user['id'], search=s, category_id=cid)
            if not courses:
                tk.Label(scroll_frame, text="No courses found.", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
                return
            for course in courses:
                self._course_card(scroll_frame, course, refresh)

        self._search_bar(self.main, refresh, cats)
        frame = tk.Frame(self.main, bg=BG)
        frame.pack(fill="both", expand=True, padx=25)
        scroll_frame = scrollable(frame)
        refresh()

    def _course_card(self, parent, course, refresh_fn):
        c = card_frame(parent)
        c.pack(fill="x", pady=5, ipady=4)

        top = tk.Frame(c, bg=CARD)
        top.pack(fill="x", padx=18, pady=(14, 4))

        # Category badge
        if course.get('category_name'):
            badge = tk.Label(top, text=f"  {course['category_name']}  ",
                             font=("Segoe UI", 8, "bold"), bg=ACCENT_LT, fg=ACCENT,
                             relief="flat", pady=2)
            badge.pack(side="right")

        tk.Label(top, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")
        desc = course['description'] or "No description provided."
        tk.Label(c, text=desc[:110] + ("..." if len(desc) > 110 else ""),
                 font=SMALL, bg=CARD, fg=MUTED, wraplength=680, justify="left").pack(anchor="w", padx=18)

        bf = tk.Frame(c, bg=CARD)
        bf.pack(anchor="w", padx=18, pady=(8, 14))
        btn(bf, "📖 Lessons", lambda crs=course: self.show_lessons(crs), small=True).pack(side="left", padx=(0, 6))
        btn(bf, "✏ Edit", lambda crs=course: self.show_edit_course(crs, refresh_fn),
            color=WARN, small=True).pack(side="left", padx=(0, 6))
        btn(bf, "🗑 Delete", lambda crs=course: self._delete_course(crs, refresh_fn),
            color=DANGER, small=True).pack(side="left")

    def _delete_course(self, course, refresh_fn):
        if messagebox.askyesno("Delete Course", f"Delete '{course['title']}' and all its content?"):
            delete_course(course['id'])
            refresh_fn()

    # ── NEW COURSE ────────────────────────────────────────
    def show_new_course(self):
        self.clear_main()
        self.page_header("Create New Course")
        cats = get_categories()

        c = card_frame(self.main)
        c.pack(padx=25, pady=5, fill="x", ipady=5)

        def lbl(text): tk.Label(c, text=text, font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(14, 4))

        lbl("COURSE TITLE")
        title_e = entry(c)
        title_e.pack(fill="x", padx=25, ipady=6)

        lbl("DESCRIPTION")
        desc_e = scrolledtext.ScrolledText(c, bg="#F8F9FC", fg=TEXT, relief="solid",
                                            font=FONT, height=4, bd=1, wrap="word")
        desc_e.pack(fill="x", padx=25)

        lbl("CATEGORY")
        cat_var = tk.StringVar(value=cats[0]['name'] if cats else "")
        cat_map = {cat['name']: cat['id'] for cat in cats}
        ttk.Combobox(c, textvariable=cat_var, values=[cat['name'] for cat in cats],
                     state="readonly", font=FONT, width=30).pack(anchor="w", padx=25)

        msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        msg.pack(pady=5)

        def save():
            t = title_e.get().strip()
            d = desc_e.get("1.0", "end").strip()
            if not t:
                msg.config(text="Title is required.")
                return
            cid = cat_map.get(cat_var.get())
            create_course(t, d, self.user['id'], cid)
            msg.config(text="✓ Course created!", fg=SUCCESS)
            self.root.after(900, self.show_courses)

        btn(c, "  Create Course  ", save, color=SUCCESS).pack(anchor="w", padx=25, pady=15)

    def show_edit_course(self, course, refresh_fn):
        self.clear_main()
        self.page_header(f"Edit Course")
        cats = get_categories()
        cat_map = {cat['name']: cat['id'] for cat in cats}
        id_to_name = {cat['id']: cat['name'] for cat in cats}

        c = card_frame(self.main)
        c.pack(padx=25, pady=5, fill="x", ipady=5)

        def lbl(t): tk.Label(c, text=t, font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(14, 4))

        lbl("COURSE TITLE")
        title_e = entry(c)
        title_e.insert(0, course['title'])
        title_e.pack(fill="x", padx=25, ipady=6)

        lbl("DESCRIPTION")
        desc_e = scrolledtext.ScrolledText(c, bg="#F8F9FC", fg=TEXT, relief="solid",
                                            font=FONT, height=4, bd=1, wrap="word")
        desc_e.insert("1.0", course['description'] or "")
        desc_e.pack(fill="x", padx=25)

        lbl("CATEGORY")
        current_cat = id_to_name.get(course.get('category_id'), cats[0]['name'] if cats else "")
        cat_var = tk.StringVar(value=current_cat)
        ttk.Combobox(c, textvariable=cat_var, values=[cat['name'] for cat in cats],
                     state="readonly", font=FONT, width=30).pack(anchor="w", padx=25)

        msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        msg.pack(pady=5)

        def save():
            t = title_e.get().strip()
            d = desc_e.get("1.0", "end").strip()
            if not t:
                msg.config(text="Title is required.")
                return
            update_course(course['id'], t, d, cat_map.get(cat_var.get()))
            msg.config(text="✓ Updated!", fg=SUCCESS)
            self.root.after(900, self.show_courses)

        bf = tk.Frame(c, bg=CARD)
        bf.pack(anchor="w", padx=25, pady=15)
        btn(bf, "Save Changes", save, color=SUCCESS).pack(side="left", padx=(0, 8))
        btn(bf, "Cancel", self.show_courses, outline=True).pack(side="left")

    # ── LESSONS ───────────────────────────────────────────
    def show_lessons(self, course):
        self.clear_main()
        self.page_header(f"Lessons — {course['title']}")

        back = tk.Frame(self.main, bg=BG)
        back.pack(anchor="w", padx=25, pady=(0, 8))
        btn(back, "← Back to Courses", self.show_courses, outline=True, small=True).pack(side="left")

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)
        scroll_frame = scrollable(outer)

        # Add form
        af = card_frame(scroll_frame)
        af.pack(fill="x", pady=(0, 10), ipady=5)
        tk.Label(af, text="ADD NEW LESSON", font=("Segoe UI", 8, "bold"), bg=CARD, fg=ACCENT).pack(anchor="w", padx=18, pady=(14, 4))
        tk.Label(af, text="TITLE", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(6, 3))
        l_title = entry(af)
        l_title.pack(fill="x", padx=18, ipady=6)
        tk.Label(af, text="CONTENT", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(10, 3))
        l_content = scrolledtext.ScrolledText(af, bg="#F8F9FC", fg=TEXT, relief="solid", font=FONT, height=5, bd=1, wrap="word")
        l_content.pack(fill="x", padx=18)
        add_msg = tk.Label(af, text="", font=SMALL, bg=CARD, fg=DANGER)
        add_msg.pack(pady=4)

        def add_l():
            t = l_title.get().strip()
            ct = l_content.get("1.0", "end").strip()
            if not t or not ct:
                add_msg.config(text="Fill both fields.")
                return
            add_lesson(course['id'], t, ct)
            self.show_lessons(course)

        btn(af, " + Add Lesson", add_l, color=SUCCESS, small=True).pack(anchor="w", padx=18, pady=(6, 14))

        # Existing lessons
        lessons = get_lessons(course['id'])
        if lessons:
            tk.Label(scroll_frame, text=f"EXISTING LESSONS  ({len(lessons)})",
                     font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", pady=(8, 4))
        for i, lesson in enumerate(lessons, 1):
            lf = card_frame(scroll_frame)
            lf.pack(fill="x", pady=3, ipady=4)
            row = tk.Frame(lf, bg=CARD)
            row.pack(fill="x", padx=18, pady=(10, 4))
            tk.Label(row, text=f"{i}.  {lesson['title']}", font=BOLD, bg=CARD, fg=TEXT).pack(side="left")
            btn(row, "Delete", lambda l=lesson: (delete_lesson(l['id']), self.show_lessons(course)),
                color=DANGER, small=True).pack(side="right")
            preview = lesson['content'][:130] + ("..." if len(lesson['content']) > 130 else "")
            tk.Label(lf, text=preview, font=SMALL, bg=CARD, fg=MUTED,
                     wraplength=730, justify="left").pack(anchor="w", padx=18, pady=(0, 10))

    # ── QUIZZES ───────────────────────────────────────────
    def show_quizzes(self):
        self.clear_main()
        self.page_header("Quiz Manager", "Create timed quizzes with pass thresholds")
        courses = get_instructor_courses(self.user['id'])

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)
        scroll_frame = scrollable(outer)

        if not courses:
            tk.Label(scroll_frame, text="Create a course first.", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
            return

        for course in courses:
            cf = card_frame(scroll_frame)
            cf.pack(fill="x", pady=6, ipady=4)
            tk.Label(cf, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(anchor="w", padx=18, pady=(12, 6))
            tk.Frame(cf, bg=BORDER, height=1).pack(fill="x", padx=18, pady=(0, 8))

            quizzes = get_quizzes(course['id'])
            for quiz in quizzes:
                qf = tk.Frame(cf, bg=ACCENT_LT)
                qf.pack(fill="x", padx=18, pady=3, ipady=5)
                ql = tk.Frame(qf, bg=ACCENT_LT)
                ql.pack(fill="x", padx=10)
                info = f"📝  {quiz['title']}   •   {len(get_questions(quiz['id']))} questions"
                if quiz.get('time_limit') and quiz['time_limit'] > 0:
                    info += f"   •   ⏱ {quiz['time_limit']}s"
                if quiz.get('pass_score') and quiz['pass_score'] > 0:
                    info += f"   •   Pass: {quiz['pass_score']}%"
                tk.Label(ql, text=info, font=("Segoe UI", 9, "bold"), bg=ACCENT_LT, fg=ACCENT).pack(side="left", pady=6)
                btn(ql, "+ Question", lambda q=quiz: self._add_question_dialog(q), small=True).pack(side="right", padx=4)
                btn(ql, "Delete", lambda q=quiz: (delete_quiz(q['id']), self.show_quizzes()),
                    color=DANGER, small=True).pack(side="right", padx=4)

            # New quiz form
            nf = tk.Frame(cf, bg=CARD)
            nf.pack(fill="x", padx=18, pady=(6, 14))
            tk.Label(nf, text="NEW QUIZ", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", pady=(4, 6))
            row1 = tk.Frame(nf, bg=CARD)
            row1.pack(anchor="w")
            title_e = entry(row1, width=25)
            title_e.insert(0, "Quiz title...")
            title_e.pack(side="left", ipady=5, padx=(0, 8))
            tk.Label(row1, text="⏱ Time(s):", font=SMALL, bg=CARD, fg=MUTED).pack(side="left")
            time_e = entry(row1, width=6)
            time_e.insert(0, "0")
            time_e.pack(side="left", ipady=5, padx=(4, 8))
            tk.Label(row1, text="✅ Pass%:", font=SMALL, bg=CARD, fg=MUTED).pack(side="left")
            pass_e = entry(row1, width=5)
            pass_e.insert(0, "0")
            pass_e.pack(side="left", ipady=5, padx=(4, 8))

            def make_quiz(te=title_e, time=time_e, ps=pass_e, c=course):
                t = te.get().strip()
                if not t or t == "Quiz title...": return
                try: tl = int(time.get())
                except: tl = 0
                try: psc = int(ps.get())
                except: psc = 0
                create_quiz(c['id'], t, tl, psc)
                self.show_quizzes()

            btn(nf, "Create Quiz", make_quiz, color=SUCCESS, small=True).pack(anchor="w", pady=6)

    def _add_question_dialog(self, quiz):
        win = tk.Toplevel(self.root)
        win.title("Add Question")
        win.geometry("520x470")
        win.configure(bg=BG)
        win.grab_set()
        tk.Frame(win, bg=ACCENT, height=3).pack(fill="x")

        tk.Label(win, text=f"Add to: {quiz['title']}", font=HEADING, bg=BG, fg=TEXT).pack(pady=(15, 10), padx=25, anchor="w")

        fields = {}
        for lbl in ["QUESTION TEXT", "OPTION A", "OPTION B", "OPTION C", "OPTION D"]:
            tk.Label(win, text=lbl, font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=25, pady=(10, 3))
            e = entry(win)
            e.pack(fill="x", padx=25, ipady=6)
            fields[lbl] = e

        tk.Label(win, text="CORRECT ANSWER", font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", padx=25, pady=(12, 4))
        correct_var = tk.StringVar(value="A")
        rf = tk.Frame(win, bg=BG)
        rf.pack(anchor="w", padx=25)
        for opt in ["A", "B", "C", "D"]:
            tk.Radiobutton(rf, text=opt, variable=correct_var, value=opt,
                           bg=BG, fg=TEXT, selectcolor=ACCENT, font=FONT,
                           activebackground=BG).pack(side="left", padx=10)

        msg = tk.Label(win, text="", font=SMALL, bg=BG, fg=DANGER)
        msg.pack(pady=5)

        def save():
            q = fields["QUESTION TEXT"].get().strip()
            opts = [fields[f"OPTION {o}"].get().strip() for o in ["A","B","C","D"]]
            if not q or not all(opts):
                msg.config(text="Fill all fields.")
                return
            add_question(quiz['id'], q, *opts, correct_var.get())
            msg.config(text="✓ Question added!", fg=SUCCESS)
            win.after(700, win.destroy)

        btn(win, "  Save Question  ", save, color=SUCCESS).pack(pady=10)

    # ── PROFILE ───────────────────────────────────────────
    def show_profile(self):
        self.clear_main()
        self.page_header("My Profile", "View and update your account details")
        user = get_user(self.user['id'])

        c = card_frame(self.main)
        c.pack(padx=25, pady=5, fill="x", ipady=5)

        # Avatar
        av = tk.Frame(c, bg=CARD)
        av.pack(anchor="w", padx=25, pady=(20, 10))
        initials = "".join(p[0].upper() for p in user['full_name'].split()[:2])
        tk.Label(av, text=initials, font=("Segoe UI", 18, "bold"),
                 bg=ACCENT, fg="white", width=4, pady=10).pack(side="left")
        info = tk.Frame(av, bg=CARD)
        info.pack(side="left", padx=15)
        tk.Label(info, text=user['full_name'], font=HEADING, bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(info, text=f"@{user['username']}  •  {user['role'].title()}",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w")
        tk.Label(info, text=f"Joined: {str(user['created_at'])[:10]}",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w")

        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=25, pady=10)

        def lbl(t): tk.Label(c, text=t, font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(12, 4))

        lbl("FULL NAME")
        name_e = entry(c)
        name_e.insert(0, user['full_name'])
        name_e.pack(fill="x", padx=25, ipady=6)

        lbl("BIO")
        bio_e = scrolledtext.ScrolledText(c, bg="#F8F9FC", fg=TEXT, relief="solid",
                                           font=FONT, height=3, bd=1, wrap="word")
        bio_e.insert("1.0", user.get('bio') or "")
        bio_e.pack(fill="x", padx=25)

        msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        msg.pack(pady=5)

        def save():
            n = name_e.get().strip()
            b = bio_e.get("1.0", "end").strip()
            if not n:
                msg.config(text="Name cannot be empty.")
                return
            update_profile(self.user['id'], n, b)
            self.user['full_name'] = n
            msg.config(text="✓ Profile updated!", fg=SUCCESS)

        btn(c, "Save Changes", save, color=SUCCESS).pack(anchor="w", padx=25, pady=(6, 6))

        # Change password
        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=25, pady=10)
        tk.Label(c, text="CHANGE PASSWORD", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=25, pady=(4, 4))
        pw_e = entry(c, show="•")
        pw_e.pack(fill="x", padx=25, ipady=6)

        pw_msg = tk.Label(c, text="", font=SMALL, bg=CARD, fg=DANGER)
        pw_msg.pack(pady=3)

        def change_pw():
            pw = pw_e.get().strip()
            if len(pw) < 4:
                pw_msg.config(text="Min 4 characters.", fg=DANGER)
                return
            change_password(self.user['id'], pw)
            pw_msg.config(text="✓ Password changed!", fg=SUCCESS)
            pw_e.delete(0, "end")

        btn(c, "Update Password", change_pw, outline=True).pack(anchor="w", padx=25, pady=(0, 20))
