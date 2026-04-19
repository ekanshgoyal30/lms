import os
from datetime import datetime

CERT_DIR = os.path.join(os.path.dirname(__file__), "certificates")

def generate_certificate(student_name, course_title):
    os.makedirs(CERT_DIR, exist_ok=True)
    safe_name = "".join(c if c.isalnum() else "_" for c in f"{student_name}_{course_title}")
    filename = os.path.join(CERT_DIR, f"cert_{safe_name}.txt")
    date_str = datetime.now().strftime("%B %d, %Y")

    content = f"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🎓  CERTIFICATE OF COMPLETION  🎓                   ║
║                                                                  ║
║  This is to certify that                                         ║
║                                                                  ║
║       {student_name.center(58)}║
║                                                                  ║
║  has successfully completed the course                           ║
║                                                                  ║
║       {course_title.center(58)}║
║                                                                  ║
║  Date: {date_str.ljust(57)}║
║                                                                  ║
║               ★  LearnPy LMS  ★                                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename, content
