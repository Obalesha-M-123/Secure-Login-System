
import sqlite3
import bcrypt

DATABASE = "users.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def create_table():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def register_user(username, email, password):
    conn = get_connection()

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    )

    try:
        conn.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


def verify_user(email, password):
    conn = get_connection()

    user = conn.execute(
        "SELECT id, username, password FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    if user and bcrypt.checkpw(
        password.encode("utf-8"),
        user[2]
    ):
        return user

    return None
