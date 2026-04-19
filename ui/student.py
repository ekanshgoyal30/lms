import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.base import BaseDashboard
from ui.theme import *
from courses import get_all_courses, get_enrolled_courses, enroll_student, is_enrolled, get_lessons
from progress import mark_lesson_complete, get_completed_lessons, get_course_progress
from quiz import get_quizzes, get_questions, save_attempt, get_attempts
from certificate import generate_certificate
from database import get_categories, update_profile, get_user, change_password

class StudentDashboard(BaseDashboard):
    ROLE_LABEL = "STUDENT PORTAL"
    NAV_ITEMS = []

    def __init__(self, user, on_logout):
        self.NAV_ITEMS = [
            ("📚   My Courses",    self.show_my_courses),
            ("🌐   Browse",        self.show_browse),
            ("📊   My Progress",   self.show_progress),
            ("👤   My Profile",   self.show_profile),
        ]
        super().__init__(user, on_logout, "LearnPy — Student Dashboard")
        self._nav_click(self.show_my_courses, "📚   My Courses")
        self.run()

    # ── Search/filter bar ─────────────────────────────────
    def _filter_bar(self, parent, on_change, categories):
        f = tk.Frame(parent, bg=BG)
        f.pack(fill="x", padx=25, pady=(0, 12))

        sf = tk.Frame(f, bg=CARD, relief="solid", bd=1,
                      highlightthickness=1, highlightbackground=BORDER)
        sf.pack(side="left", padx=(0, 10))
        tk.Label(sf, text="🔍", bg=CARD, fg=MUTED, font=FONT).pack(side="left", padx=(8, 4))
        self._sv = tk.StringVar()
        se = tk.Entry(sf, textvariable=self._sv, bg=CARD, fg=TEXT,
                      relief="flat", font=FONT, width=22, insertbackground=ACCENT)
        se.pack(side="left", ipady=6, padx=(0, 8))
        se.bind("<KeyRelease>", lambda e: on_change())

        self._cv = tk.StringVar(value="All Categories")
        names = ["All Categories"] + [c['name'] for c in categories]
        self._cmap = {c['name']: c['id'] for c in categories}
        dd = ttk.Combobox(f, textvariable=self._cv, values=names, state="readonly", font=FONT, width=18)
        dd.pack(side="left")
        dd.bind("<<ComboboxSelected>>", lambda e: on_change())

    def _filters(self):
        s = getattr(self, '_sv', None)
        cv = getattr(self, '_cv', None)
        search = s.get().strip() if s else ""
        cat_name = cv.get() if cv else "All Categories"
        cat_id = self._cmap.get(cat_name) if hasattr(self, '_cmap') else None
        return search, cat_id

    # ── MY COURSES ────────────────────────────────────────
    def show_my_courses(self):
        self.clear_main()
        self.page_header("My Courses", "Your enrolled courses")
        cats = get_categories()

        def refresh():
            for w in sf.winfo_children(): w.destroy()
            s, cid = self._filters()
            courses = get_enrolled_courses(self.user['id'], search=s, category_id=cid)
            if not courses:
                tk.Label(sf, text="No courses found. Browse to enroll!", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
                return
            for course in courses:
                self._my_course_card(sf, course)

        self._filter_bar(self.main, refresh, cats)
        frame = tk.Frame(self.main, bg=BG)
        frame.pack(fill="both", expand=True, padx=25)
        sf = scrollable(frame)
        refresh()

    def _my_course_card(self, parent, course):
        done, total = get_course_progress(self.user['id'], course['id'])
        pct = int(done / total * 100) if total > 0 else 0

        c = card_frame(parent)
        c.pack(fill="x", pady=5, ipady=4)

        top = tk.Frame(c, bg=CARD)
        top.pack(fill="x", padx=18, pady=(14, 4))

        if course.get('category_name'):
            tk.Label(top, text=f"  {course['category_name']}  ",
                     font=("Segoe UI", 8, "bold"), bg=ACCENT_LT, fg=ACCENT,
                     relief="flat", pady=2).pack(side="right")
        if pct == 100:
            tk.Label(top, text="✓ Complete", font=("Segoe UI", 9, "bold"),
                     bg=SUCCESS_LT, fg=SUCCESS).pack(side="right", padx=6)

        tk.Label(top, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")
        tk.Label(c, text=f"By {course['instructor_name']}", font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w", padx=18)

        pf = tk.Frame(c, bg=CARD)
        pf.pack(anchor="w", padx=18, pady=6)
        pb = progress_bar(pf, pct)
        pb.pack(side="left")
        tk.Label(pf, text=f"  {pct}%  ({done}/{total} lessons)",
                 font=("Segoe UI", 8), bg=CARD, fg=MUTED).pack(side="left")

        bf = tk.Frame(c, bg=CARD)
        bf.pack(anchor="w", padx=18, pady=(0, 14))
        btn(bf, "▶  Continue", lambda crs=course: self.open_course(crs), small=True).pack(side="left", padx=(0, 6))
        if pct == 100:
            btn(bf, "🏆 Certificate", lambda crs=course: self._get_certificate(crs),
                color=SUCCESS, small=True).pack(side="left")

    # ── BROWSE ───────────────────────────────────────────
    def show_browse(self):
        self.clear_main()
        self.page_header("Browse Courses", "Discover and enroll in new courses")
        cats = get_categories()

        def refresh():
            for w in sf.winfo_children(): w.destroy()
            s, cid = self._filters()
            courses = get_all_courses(search=s, category_id=cid)
            if not courses:
                tk.Label(sf, text="No courses found.", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
                return
            for course in courses:
                self._browse_card(sf, course, refresh)

        self._filter_bar(self.main, refresh, cats)
        frame = tk.Frame(self.main, bg=BG)
        frame.pack(fill="both", expand=True, padx=25)
        sf = scrollable(frame)
        refresh()

    def _browse_card(self, parent, course, refresh_fn):
        enrolled = is_enrolled(self.user['id'], course['id'])
        lessons = get_lessons(course['id'])
        c = card_frame(parent)
        c.pack(fill="x", pady=5, ipady=4)

        top = tk.Frame(c, bg=CARD)
        top.pack(fill="x", padx=18, pady=(14, 4))
        if course.get('category_name'):
            tk.Label(top, text=f"  {course['category_name']}  ",
                     font=("Segoe UI", 8, "bold"), bg=ACCENT_LT, fg=ACCENT, pady=2).pack(side="right")
        status = ("✓ Enrolled", SUCCESS_LT, SUCCESS) if enrolled else ("Not enrolled", BG, MUTED)
        tk.Label(top, text=status[0], font=("Segoe UI", 8, "bold"),
                 bg=status[1], fg=status[2]).pack(side="right", padx=6)
        tk.Label(top, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")

        tk.Label(c, text=f"By {course['instructor_name']}  •  {len(lessons)} lessons",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w", padx=18)
        if course.get('description'):
            desc = course['description'][:120] + ("..." if len(course['description']) > 120 else "")
            tk.Label(c, text=desc, font=SMALL, bg=CARD, fg=MUTED,
                     wraplength=680, justify="left").pack(anchor="w", padx=18, pady=(3, 0))

        bf = tk.Frame(c, bg=CARD)
        bf.pack(anchor="w", padx=18, pady=(8, 14))
        if enrolled:
            btn(bf, "▶  Open Course", lambda crs=course: self.open_course(crs), small=True).pack(side="left")
        else:
            btn(bf, "Enroll Now", lambda crs=course: self._enroll(crs, refresh_fn),
                color=SUCCESS, small=True).pack(side="left")

    def _enroll(self, course, refresh_fn):
        if messagebox.askyesno("Enroll", f"Enroll in '{course['title']}'?"):
            enroll_student(self.user['id'], course['id'])
            refresh_fn()

    # ── COURSE VIEW ──────────────────────────────────────
    def open_course(self, course):
        self.clear_main()
        self.page_header(course['title'], f"By {course['instructor_name']}")

        back = tk.Frame(self.main, bg=BG)
        back.pack(anchor="w", padx=25, pady=(0, 8))
        btn(back, "← My Courses", self.show_my_courses, outline=True, small=True).pack(side="left")

        lessons = get_lessons(course['id'])
        quizzes = get_quizzes(course['id'])
        completed = get_completed_lessons(self.user['id'], course['id'])
        done, total = get_course_progress(self.user['id'], course['id'])
        pct = int(done / total * 100) if total > 0 else 0

        # Progress strip
        ps = tk.Frame(self.main, bg=CARD, relief="solid", bd=1,
                      highlightthickness=1, highlightbackground=BORDER)
        ps.pack(fill="x", padx=25, pady=(0, 10))
        pi = tk.Frame(ps, bg=CARD)
        pi.pack(fill="x", padx=18, pady=12)
        tk.Label(pi, text=f"Course Progress  {pct}%", font=BOLD, bg=CARD, fg=TEXT).pack(anchor="w")
        pb = progress_bar(pi, pct, width=450)
        pb.pack(anchor="w", pady=4)
        if pct == 100:
            tk.Label(pi, text="🎉 Course Complete! You can now download your certificate.",
                     font=SMALL, bg=CARD, fg=SUCCESS).pack(anchor="w")

        frame = tk.Frame(self.main, bg=BG)
        frame.pack(fill="both", expand=True, padx=25)
        sf = scrollable(frame)

        # Lessons section
        if lessons:
            tk.Label(sf, text="LESSONS", font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", pady=(10, 5))
        for i, lesson in enumerate(lessons, 1):
            is_done = lesson['id'] in completed
            lf = card_frame(sf)
            lf.pack(fill="x", pady=3, ipady=2)
            if is_done:
                tk.Frame(lf, bg=SUCCESS, width=4).pack(side="left", fill="y")
            row = tk.Frame(lf, bg=CARD)
            row.pack(fill="x", padx=15, pady=(10, 4))
            color = SUCCESS if is_done else TEXT
            mark = "✓ " if is_done else f"{i}. "
            tk.Label(row, text=f"{mark}{lesson['title']}", font=BOLD, bg=CARD, fg=color).pack(side="left")
            if not is_done:
                btn(row, "Mark Complete",
                    lambda l=lesson, crs=course: (mark_lesson_complete(self.user['id'], l['id']),
                                                   self.open_course(crs)),
                    color=SUCCESS, small=True).pack(side="right")
            tk.Button(row, text="Read →", font=("Segoe UI", 9, "bold"),
                      command=lambda l=lesson: self._read_lesson(l),
                      bg=CARD, fg=ACCENT, relief="flat", cursor="hand2").pack(side="right", padx=8)
            preview = lesson['content'][:110] + ("..." if len(lesson['content']) > 110 else "")
            tk.Label(lf, text=preview, font=SMALL, bg=CARD, fg=MUTED,
                     wraplength=720, justify="left").pack(anchor="w", padx=15, pady=(0, 10))

        # Quizzes section
        if quizzes:
            tk.Label(sf, text="QUIZZES", font=("Segoe UI", 8, "bold"), bg=BG, fg=MUTED).pack(anchor="w", pady=(18, 5))
        for quiz in quizzes:
            attempts = get_attempts(self.user['id'], quiz['id'])
            qf = card_frame(sf)
            qf.pack(fill="x", pady=3, ipady=2)
            row = tk.Frame(qf, bg=CARD)
            row.pack(fill="x", padx=15, pady=(10, 4))
            tl = f"  ⏱ {quiz['time_limit']}s" if quiz.get('time_limit') and quiz['time_limit'] > 0 else ""
            ps_txt = f"  ✅ Pass: {quiz['pass_score']}%" if quiz.get('pass_score') and quiz['pass_score'] > 0 else ""
            tk.Label(row, text=f"📝  {quiz['title']}{tl}{ps_txt}", font=BOLD, bg=CARD, fg=TEXT).pack(side="left")
            btn(row, "Take Quiz", lambda q=quiz, crs=course: self._take_quiz(q, crs), small=True).pack(side="right")
            if attempts:
                best = max(a['score'] / a['total'] * 100 for a in attempts)
                passed = quiz.get('pass_score', 0) == 0 or best >= quiz['pass_score']
                color = SUCCESS if passed else DANGER
                tk.Label(qf, text=f"  Best score: {best:.0f}%  •  {len(attempts)} attempt(s)",
                         font=("Segoe UI", 9, "bold"), bg=CARD, fg=color).pack(anchor="w", padx=15, pady=(0, 8))

    def _read_lesson(self, lesson):
        win = tk.Toplevel(self.root)
        win.title(lesson['title'])
        win.geometry("720x520")
        win.configure(bg=BG)
        tk.Frame(win, bg=ACCENT, height=3).pack(fill="x")
        tk.Label(win, text=lesson['title'], font=TITLE, bg=BG, fg=TEXT).pack(pady=(20, 5), padx=30, anchor="w")
        tk.Frame(win, bg=BORDER, height=1).pack(fill="x", padx=30, pady=8)
        t = scrolledtext.ScrolledText(win, bg=CARD, fg=TEXT, font=FONT, wrap="word",
                                       relief="solid", bd=1, padx=15, pady=15)
        t.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        t.insert("1.0", lesson['content'])
        t.config(state="disabled")

    # ── QUIZ WITH TIMER ───────────────────────────────────
    def _take_quiz(self, quiz, course):
        questions = get_questions(quiz['id'])
        if not questions:
            messagebox.showinfo("Quiz", "No questions yet.")
            return

        win = tk.Toplevel(self.root)
        win.title(f"Quiz: {quiz['title']}")
        win.geometry("640x580")
        win.configure(bg=BG)
        win.grab_set()
        tk.Frame(win, bg=ACCENT, height=3).pack(fill="x")

        # Header with timer
        hf = tk.Frame(win, bg=CARD, relief="solid", bd=1,
                      highlightthickness=1, highlightbackground=BORDER)
        hf.pack(fill="x", padx=20, pady=(15, 5))
        hl = tk.Frame(hf, bg=CARD)
        hl.pack(fill="x", padx=18, pady=10)
        tk.Label(hl, text=quiz['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")

        time_limit = quiz.get('time_limit', 0) or 0
        timer_label = tk.Label(hl, text="", font=("Segoe UI", 11, "bold"), bg=CARD, fg=ACCENT)
        timer_label.pack(side="right")

        # Questions scroll
        outer = tk.Frame(win, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=5)
        qframe = scrollable(outer)

        answers = {}
        for i, q in enumerate(questions, 1):
            qf = card_frame(qframe)
            qf.pack(fill="x", pady=4, ipady=4)
            tk.Label(qf, text=f"Q{i}.  {q['question_text']}", font=BOLD, bg=CARD, fg=TEXT,
                     wraplength=560, justify="left").pack(anchor="w", padx=15, pady=(12, 6))
            var = tk.StringVar()
            answers[q['id']] = var
            for opt in ["A", "B", "C", "D"]:
                text = q[f'option_{opt.lower()}']
                tk.Radiobutton(qf, text=f"  {opt}.  {text}", variable=var, value=opt,
                               bg=CARD, fg=TEXT, selectcolor=ACCENT, font=FONT,
                               activebackground=CARD).pack(anchor="w", padx=20, pady=2)

        # Timer logic
        self._timer_running = True

        def submit():
            self._timer_running = False
            score = sum(1 for q in questions if answers[q['id']].get() == q['correct_option'])
            save_attempt(self.user['id'], quiz['id'], score, len(questions))
            pct = score / len(questions) * 100
            pass_score = quiz.get('pass_score', 0) or 0
            passed = pass_score == 0 or pct >= pass_score
            win.destroy()
            result_msg = f"Score: {score}/{len(questions)}  ({pct:.0f}%)\n\n"
            if passed:
                result_msg += "✅ PASSED!" if pass_score > 0 else ("🎉 Excellent!" if pct >= 80 else "👍 Good effort!")
            else:
                result_msg += f"❌ Not passed. Required: {pass_score}%"
            messagebox.showinfo("Quiz Result", result_msg)
            self.open_course(course)

        def tick(remaining):
            if not self._timer_running: return
            if remaining <= 0:
                timer_label.config(text="⏱ Time's up!", fg=DANGER)
                win.after(800, submit)
                return
            color = DANGER if remaining <= 10 else (WARN if remaining <= 30 else ACCENT)
            timer_label.config(text=f"⏱ {remaining}s", fg=color)
            win.after(1000, lambda: tick(remaining - 1))

        if time_limit > 0:
            tick(time_limit)
        else:
            timer_label.config(text="No time limit", fg=MUTED)

        win.protocol("WM_DELETE_WINDOW", lambda: (setattr(self, '_timer_running', False), win.destroy()))
        btn(win, "  Submit Answers  ", submit, color=SUCCESS).pack(pady=12)

    # ── PROGRESS ─────────────────────────────────────────
    def show_progress(self):
        self.clear_main()
        self.page_header("My Progress", "Track your learning across all courses")
        courses = get_enrolled_courses(self.user['id'])

        outer = tk.Frame(self.main, bg=BG)
        outer.pack(fill="both", expand=True, padx=25)
        sf = scrollable(outer)

        if not courses:
            tk.Label(sf, text="No courses enrolled yet.", font=FONT, bg=BG, fg=MUTED).pack(pady=30)
            return

        total_courses = len(courses)
        completed_courses = 0
        for course in courses:
            done, total = get_course_progress(self.user['id'], course['id'])
            pct = int(done / total * 100) if total > 0 else 0
            if pct == 100: completed_courses += 1

            c = card_frame(sf)
            c.pack(fill="x", pady=5, ipady=4)
            top = tk.Frame(c, bg=CARD)
            top.pack(fill="x", padx=18, pady=(14, 6))
            tk.Label(top, text=course['title'], font=HEADING, bg=CARD, fg=TEXT).pack(side="left")
            if pct == 100:
                tk.Label(top, text="✓ Complete", font=("Segoe UI", 9, "bold"),
                         bg=SUCCESS_LT, fg=SUCCESS).pack(side="right")

            pf = tk.Frame(c, bg=CARD)
            pf.pack(anchor="w", padx=18, pady=4)
            pb = progress_bar(pf, pct)
            pb.pack(side="left")
            tk.Label(pf, text=f"  {pct}%  ({done}/{total} lessons)",
                     font=("Segoe UI", 8), bg=CARD, fg=MUTED).pack(side="left")

            quizzes = get_quizzes(course['id'])
            for quiz in quizzes:
                attempts = get_attempts(self.user['id'], quiz['id'])
                if attempts:
                    best = max(a['score'] / a['total'] * 100 for a in attempts)
                    tk.Label(c, text=f"  📝 {quiz['title']}: Best {best:.0f}%  ({len(attempts)} attempts)",
                             font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w", padx=18)

            bf = tk.Frame(c, bg=CARD)
            bf.pack(anchor="w", padx=18, pady=(6, 14))
            btn(bf, "Open Course", lambda crs=course: self.open_course(crs),
                outline=True, small=True).pack(side="left", padx=(0, 6))
            if pct == 100:
                btn(bf, "🏆 Certificate", lambda crs=course: self._get_certificate(crs),
                    color=SUCCESS, small=True).pack(side="left")

        # Summary card
        sc = card_frame(sf)
        sc.pack(fill="x", pady=(15, 5), ipady=4)
        tk.Label(sc, text="SUMMARY", font=("Segoe UI", 8, "bold"), bg=CARD, fg=MUTED).pack(anchor="w", padx=18, pady=(14, 8))
        row = tk.Frame(sc, bg=CARD)
        row.pack(fill="x", padx=18, pady=(0, 14))
        for label_text, val in [("Enrolled", total_courses), ("Completed", completed_courses),
                                  ("In Progress", total_courses - completed_courses)]:
            box = tk.Frame(row, bg=ACCENT_LT, padx=20, pady=10)
            box.pack(side="left", padx=(0, 10))
            tk.Label(box, text=str(val), font=("Segoe UI", 18, "bold"), bg=ACCENT_LT, fg=ACCENT).pack()
            tk.Label(box, text=label_text, font=SMALL, bg=ACCENT_LT, fg=MUTED).pack()

    def _get_certificate(self, course):
        done, total = get_course_progress(self.user['id'], course['id'])
        if total > 0 and done < total:
            messagebox.showwarning("Not Complete", "Complete all lessons first.")
            return
        path, content = generate_certificate(self.user['full_name'], course['title'])
        win = tk.Toplevel(self.root)
        win.title("Certificate")
        win.geometry("640x380")
        win.configure(bg=BG)
        tk.Frame(win, bg=SUCCESS, height=3).pack(fill="x")
        tk.Label(win, text="🎓 Certificate of Completion", font=TITLE, bg=BG, fg=SUCCESS).pack(pady=(15, 5))
        t = scrolledtext.ScrolledText(win, bg=CARD, fg=SUCCESS, font=("Courier New", 9),
                                       relief="solid", bd=1, height=12)
        t.pack(fill="both", expand=True, padx=20, pady=10)
        t.insert("1.0", content)
        t.config(state="disabled")
        tk.Label(win, text=f"Saved: {path}", font=SMALL, bg=BG, fg=MUTED).pack(pady=5)

    # ── PROFILE ───────────────────────────────────────────
    def show_profile(self):
        self.clear_main()
        self.page_header("My Profile", "Manage your account")
        user = get_user(self.user['id'])

        c = card_frame(self.main)
        c.pack(padx=25, pady=5, fill="x", ipady=5)

        av = tk.Frame(c, bg=CARD)
        av.pack(anchor="w", padx=25, pady=(20, 10))
        initials = "".join(p[0].upper() for p in user['full_name'].split()[:2])
        tk.Label(av, text=initials, font=("Segoe UI", 18, "bold"),
                 bg=ACCENT, fg="white", width=4, pady=10).pack(side="left")
        info = tk.Frame(av, bg=CARD)
        info.pack(side="left", padx=15)
        tk.Label(info, text=user['full_name'], font=HEADING, bg=CARD, fg=TEXT).pack(anchor="w")
        tk.Label(info, text=f"@{user['username']}  •  Student",
                 font=SMALL, bg=CARD, fg=MUTED).pack(anchor="w")

        # Stats strip
        courses = get_enrolled_courses(self.user['id'])
        completed = sum(1 for crs in courses
                        if get_course_progress(self.user['id'], crs['id'])[0] ==
                           get_course_progress(self.user['id'], crs['id'])[1] and
                           get_course_progress(self.user['id'], crs['id'])[1] > 0)
        stat_row = tk.Frame(c, bg=ACCENT_LT)
        stat_row.pack(fill="x", padx=25, pady=10)
        for lbl_txt, val in [("Enrolled", len(courses)), ("Completed", completed)]:
            sb = tk.Frame(stat_row, bg=ACCENT_LT, padx=20, pady=8)
            sb.pack(side="left")
            tk.Label(sb, text=str(val), font=("Segoe UI", 16, "bold"), bg=ACCENT_LT, fg=ACCENT).pack()
            tk.Label(sb, text=lbl_txt, font=SMALL, bg=ACCENT_LT, fg=MUTED).pack()

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

        btn(c, "Save Changes", save, color=SUCCESS).pack(anchor="w", padx=25, pady=(0, 6))

        tk.Frame(c, bg=BORDER, height=1).pack(fill="x", padx=25, pady=10)
        lbl("NEW PASSWORD")
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
