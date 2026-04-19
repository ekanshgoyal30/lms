import hashlib
from database import get_connection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, role, full_name):
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute(
            "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
            (username, hash_password(password), role, full_name)
        )
        conn.commit()
        return True, "Registration successful!"
    except Exception as e:
        if "UNIQUE" in str(e):
            return False, "Username already exists."
        return False, str(e)
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    if user:
        return True, dict(user)
    return False, "Invalid username or password."
