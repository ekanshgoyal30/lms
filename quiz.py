from database import get_connection

def create_quiz(course_id, title, time_limit=0, pass_score=0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO quizzes (course_id,title,time_limit,pass_score) VALUES (?,?,?,?)",
              (course_id, title, time_limit, pass_score))
    quiz_id = c.lastrowid
    conn.commit()
    conn.close()
    return quiz_id

def add_question(quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO questions (quiz_id,question_text,option_a,option_b,option_c,option_d,correct_option)
                 VALUES (?,?,?,?,?,?,?)""",
              (quiz_id, question_text, option_a, option_b, option_c, option_d, correct_option.upper()))
    conn.commit()
    conn.close()

def get_quizzes(course_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM quizzes WHERE course_id=?", (course_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def get_questions(quiz_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE quiz_id=?", (quiz_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def save_attempt(student_id, quiz_id, score, total):
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO quiz_attempts (student_id,quiz_id,score,total) VALUES (?,?,?,?)",
              (student_id, quiz_id, score, total))
    conn.commit()
    conn.close()

def get_attempts(student_id, quiz_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""SELECT score,total,attempted_at FROM quiz_attempts
                 WHERE student_id=? AND quiz_id=? ORDER BY attempted_at DESC""",
              (student_id, quiz_id))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def delete_quiz(quiz_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE quiz_id=?", (quiz_id,))
    c.execute("DELETE FROM quiz_attempts WHERE quiz_id=?", (quiz_id,))
    c.execute("DELETE FROM quizzes WHERE id=?", (quiz_id,))
    conn.commit()
    conn.close()
