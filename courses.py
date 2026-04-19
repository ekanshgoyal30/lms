from database import get_connection

# ── Courses ──────────────────────────────────────────────

def create_course(title, description, instructor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO courses (title, description, instructor_id) VALUES (?, ?, ?)",
              (title, description, instructor_id))
    conn.commit()
    conn.close()

def get_all_courses():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT courses.*, users.full_name as instructor_name
        FROM courses JOIN users ON courses.instructor_id = users.id
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_instructor_courses(instructor_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM courses WHERE instructor_id=?", (instructor_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def update_course(course_id, title, description):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE courses SET title=?, description=? WHERE id=?",
              (title, description, course_id))
    conn.commit()
    conn.close()

def delete_course(course_id):
    conn = get_connection()
    c = conn.cursor()
    # cascade delete lessons, quizzes, enrollments
    c.execute("DELETE FROM lesson_progress WHERE lesson_id IN (SELECT id FROM lessons WHERE course_id=?)", (course_id,))
    c.execute("DELETE FROM lessons WHERE course_id=?", (course_id,))
    quiz_ids = [r[0] for r in c.execute("SELECT id FROM quizzes WHERE course_id=?", (course_id,)).fetchall()]
    for qid in quiz_ids:
        c.execute("DELETE FROM questions WHERE quiz_id=?", (qid,))
        c.execute("DELETE FROM quiz_attempts WHERE quiz_id=?", (qid,))
    c.execute("DELETE FROM quizzes WHERE course_id=?", (course_id,))
    c.execute("DELETE FROM enrollments WHERE course_id=?", (course_id,))
    c.execute("DELETE FROM courses WHERE id=?", (course_id,))
    conn.commit()
    conn.close()

# ── Lessons ──────────────────────────────────────────────

def add_lesson(course_id, title, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?", (course_id,))
    order_num = c.fetchone()[0] + 1
    c.execute("INSERT INTO lessons (course_id, title, content, order_num) VALUES (?, ?, ?, ?)",
              (course_id, title, content, order_num))
    conn.commit()
    conn.close()

def get_lessons(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM lessons WHERE course_id=? ORDER BY order_num", (course_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_lesson(lesson_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM lesson_progress WHERE lesson_id=?", (lesson_id,))
    c.execute("DELETE FROM lessons WHERE id=?", (lesson_id,))
    conn.commit()
    conn.close()

# ── Enrollment ────────────────────────────────────────────

def enroll_student(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                  (student_id, course_id))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def get_enrolled_courses(student_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT courses.*, users.full_name as instructor_name
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        JOIN users ON courses.instructor_id = users.id
        WHERE enrollments.student_id=?
    """, (student_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def is_enrolled(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?",
              (student_id, course_id))
    result = c.fetchone() is not None
    conn.close()
    return result
