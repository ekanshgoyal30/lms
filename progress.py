from database import get_connection
from datetime import datetime

def mark_lesson_complete(student_id, lesson_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO lesson_progress (student_id, lesson_id, completed, completed_at)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(student_id, lesson_id) DO UPDATE SET completed=1, completed_at=?
    """, (student_id, lesson_id, datetime.now(), datetime.now()))
    conn.commit()
    conn.close()

def get_completed_lessons(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT lesson_id FROM lesson_progress
        WHERE student_id=? AND completed=1
        AND lesson_id IN (SELECT id FROM lessons WHERE course_id=?)
    """, (student_id, course_id))
    ids = {r[0] for r in c.fetchall()}
    conn.close()
    return ids

def get_course_progress(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?", (course_id,))
    total = c.fetchone()[0]
    if total == 0:
        conn.close()
        return 0, 0
    c.execute("""
        SELECT COUNT(*) FROM lesson_progress
        WHERE student_id=? AND completed=1
        AND lesson_id IN (SELECT id FROM lessons WHERE course_id=?)
    """, (student_id, course_id))
    done = c.fetchone()[0]
    conn.close()
    return done, total
