import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db

def start():
    init_db()

    def on_login(user):
        if user['role'] == 'admin':
            from ui.admin_ui import AdminDashboard
            AdminDashboard(user, start)
        elif user['role'] == 'instructor':
            from ui.instructor_ui import InstructorDashboard
            InstructorDashboard(user, start)
        else:
            from ui.student_ui import StudentDashboard
            StudentDashboard(user, start)

    from ui.login_ui import AuthWindow
    AuthWindow(on_login)

if __name__ == "__main__":
    start()
