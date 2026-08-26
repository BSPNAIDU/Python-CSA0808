import sqlite3
from passlib.context import CryptContext

DATABASE_NAME = "database.db"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def hash_password(password):
    return pwd_context.hash(str(password))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(str(plain_password), hashed_password)


def register_user(fullname, email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    if cursor.fetchone():
        conn.close()
        return {
            "status": "error",
            "message": "Email already exists"
        }

    hashed = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users(fullname,email,password)
        VALUES(?,?,?)
        """,
        (
            fullname,
            email,
            hashed
        )
    )

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "message": "Registration Successful"
    }


def login_user(email, password):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return {
            "status": "error",
            "message": "User not found"
        }

    if verify_password(password, user[3]):

        return {
            "status": "success",
            "message": "Login Successful",
            "user": {
                "id": user[0],
                "fullname": user[1],
                "email": user[2]
            }
        }

    return {
        "status": "error",
        "message": "Invalid Password"
    }