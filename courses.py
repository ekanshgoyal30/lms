from database import get_connection

def create_course(title, description, instructor_id, category_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO courses (title,description,instructor_id,category_id) VALUES (?,?,?,?)",
              (title, description, instructor_id, category_id))
    conn.commit()
    conn.close()

def get_all_courses(search="", category_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT courses.*, users.full_name as instructor_name,
               categories.name as category_name
        FROM courses
        JOIN users ON courses.instructor_id = users.id
        LEFT JOIN categories ON courses.category_id = categories.id
        WHERE 1=1
    """
    params = []
    if search:
        query += " AND (courses.title LIKE ? OR courses.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        query += " AND courses.category_id = ?"
        params.append(category_id)
    query += " ORDER BY courses.created_at DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_instructor_courses(instructor_id, search="", category_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT courses.*, categories.name as category_name
        FROM courses
        LEFT JOIN categories ON courses.category_id = categories.id
        WHERE courses.instructor_id=?
    """
    params = [instructor_id]
    if search:
        query += " AND (courses.title LIKE ? OR courses.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        query += " AND courses.category_id=?"
        params.append(category_id)
    query += " ORDER BY courses.created_at DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def update_course(course_id, title, description, category_id=None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE courses SET title=?,description=?,category_id=? WHERE id=?",
              (title, description, category_id, course_id))
    conn.commit()
    conn.close()

def delete_course(course_id):
    conn = get_connection()
    c = conn.cursor()
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

def add_lesson(course_id, title, content):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM lessons WHERE course_id=?", (course_id,))
    order_num = c.fetchone()[0] + 1
    c.execute("INSERT INTO lessons (course_id,title,content,order_num) VALUES (?,?,?,?)",
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

def enroll_student(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO enrollments (student_id,course_id) VALUES (?,?)", (student_id, course_id))
        conn.commit()
        return True
    except: return False
    finally: conn.close()

def get_enrolled_courses(student_id, search="", category_id=None):
    conn = get_connection()
    c = conn.cursor()
    query = """
        SELECT courses.*, users.full_name as instructor_name,
               categories.name as category_name
        FROM courses
        JOIN enrollments ON courses.id = enrollments.course_id
        JOIN users ON courses.instructor_id = users.id
        LEFT JOIN categories ON courses.category_id = categories.id
        WHERE enrollments.student_id=?
    """
    params = [student_id]
    if search:
        query += " AND (courses.title LIKE ? OR courses.description LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if category_id:
        query += " AND courses.category_id=?"
        params.append(category_id)
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def is_enrolled(student_id, course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM enrollments WHERE student_id=? AND course_id=?", (student_id, course_id))
    result = c.fetchone() is not None
    conn.close()
    return result
