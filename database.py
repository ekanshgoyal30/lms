import sqlite3
import os
import hashlib

DB_PATH = os.path.join(os.path.dirname(__file__), "lms.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            bio TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    try: c.execute("ALTER TABLE users ADD COLUMN bio TEXT DEFAULT ''")
    except: pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            instructor_id INTEGER NOT NULL,
            category_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(instructor_id) REFERENCES users(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    try: c.execute("ALTER TABLE courses ADD COLUMN category_id INTEGER")
    except: pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS lessons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            order_num INTEGER DEFAULT 0,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS lesson_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            lesson_id INTEGER NOT NULL,
            completed INTEGER DEFAULT 0,
            completed_at TIMESTAMP,
            UNIQUE(student_id, lesson_id),
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(lesson_id) REFERENCES lessons(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            time_limit INTEGER DEFAULT 0,
            pass_score INTEGER DEFAULT 0,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    """)
    try: c.execute("ALTER TABLE quizzes ADD COLUMN time_limit INTEGER DEFAULT 0")
    except: pass
    try: c.execute("ALTER TABLE quizzes ADD COLUMN pass_score INTEGER DEFAULT 0")
    except: pass

    c.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_option TEXT NOT NULL,
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
        )
    """)

    # Seed categories
    for cat in ["Programming","Data Science","Mathematics","Web Development",
                "Cybersecurity","Artificial Intelligence","General"]:
        try: c.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        except: pass

    # Seed admin account
    try:
        c.execute("INSERT INTO users (username,password,role,full_name) VALUES (?,?,'admin','Administrator')",
                  ("admin", hashlib.sha256("admin123".encode()).hexdigest()))
    except: pass

    conn.commit()
    conn.close()

# ── User / Admin ──────────────────────────────────────────

def get_all_users():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id,username,full_name,role,created_at FROM users ORDER BY created_at DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

def get_platform_stats():
    conn = get_connection()
    c = conn.cursor()
    s = {}
    s['students']    = c.execute("SELECT COUNT(*) FROM users WHERE role='student'").fetchone()[0]
    s['instructors'] = c.execute("SELECT COUNT(*) FROM users WHERE role='instructor'").fetchone()[0]
    s['courses']     = c.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    s['enrollments'] = c.execute("SELECT COUNT(*) FROM enrollments").fetchone()[0]
    s['attempts']    = c.execute("SELECT COUNT(*) FROM quiz_attempts").fetchone()[0]
    s['lessons']     = c.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
    conn.close()
    return s

# ── Categories ────────────────────────────────────────────

def get_categories():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM categories ORDER BY name")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_category(name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def delete_category(cat_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM categories WHERE id=?", (cat_id,))
    conn.commit()
    conn.close()

# ── Profile ───────────────────────────────────────────────

def update_profile(user_id, full_name, bio):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET full_name=?, bio=? WHERE id=?", (full_name, bio, user_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def change_password(user_id, new_password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?",
              (hashlib.sha256(new_password.encode()).hexdigest(), user_id))
    conn.commit()
    conn.close()
