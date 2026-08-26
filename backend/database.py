import sqlite3
from passlib.context import CryptContext

# =====================================================
# Database Configuration
# =====================================================

DATABASE_NAME = "database.db"

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# =====================================================
# Database Connection
# =====================================================

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# Create Users Table
# =====================================================

def create_users_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        fullname TEXT NOT NULL,

        email TEXT UNIQUE NOT NULL,

        password TEXT NOT NULL

    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# Create Analysis History Table
# =====================================================

def create_analysis_table():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        user_id INTEGER NOT NULL,

        topic TEXT NOT NULL,

        transcription TEXT NOT NULL,

        semantic_score REAL,

        fluency_score REAL,

        overall_score REAL,

        feedback TEXT,

        pdf_path TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(user_id) REFERENCES users(id)

    )
    """)

    conn.commit()
    conn.close()


# =====================================================
# Create Tables Automatically
# =====================================================

create_users_table()
create_analysis_table()


# =====================================================
# Password Functions
# =====================================================

def hash_password(password):
    return pwd_context.hash(str(password))


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(str(plain_password), hashed_password)


# =====================================================
# Register User
# =====================================================

def register_user(fullname, email, password):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        if cursor.fetchone():

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

        return {
            "status": "success",
            "message": "Registration Successful"
        }

    except sqlite3.Error as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        conn.close()


# =====================================================
# Login User
# =====================================================

def login_user(email, password):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        )

        user = cursor.fetchone()

        if user is None:

            return {
                "status": "error",
                "message": "User not found"
            }

        if verify_password(password, user["password"]):

            return {
                "status": "success",
                "message": "Login Successful",
                "user": {
                    "id": user["id"],
                    "fullname": user["fullname"],
                    "email": user["email"]
                }
            }

        return {
            "status": "error",
            "message": "Invalid Password"
        }

    except sqlite3.Error as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        conn.close()


# =====================================================
# Get User by Email
# =====================================================

def get_user(email):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email=?",
        (email,)
    )

    user = cursor.fetchone()

    conn.close()

    return user


# =====================================================
# Save Analysis Result
# =====================================================

def save_analysis(
    user_id,
    topic,
    transcription,
    semantic_score,
    fluency_score,
    overall_score,
    feedback,
    pdf_path
):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO analysis_history(

                user_id,

                topic,

                transcription,

                semantic_score,

                fluency_score,

                overall_score,

                feedback,

                pdf_path

            )
            VALUES(?,?,?,?,?,?,?,?)
            """,
            (
                user_id,
                topic,
                transcription,
                semantic_score,
                fluency_score,
                overall_score,
                feedback,
                pdf_path
            )
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Analysis Saved Successfully"
        }

    except sqlite3.Error as e:

        return {
            "status": "error",
            "message": str(e)
        }

    finally:

        conn.close()


# =====================================================
# Get User Analysis History
# =====================================================

def get_user_history(user_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *

        FROM analysis_history

        WHERE user_id=?

        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    history = cursor.fetchall()

    conn.close()

    return history


# =====================================================
# Get Single Analysis Report
# =====================================================

def get_analysis(report_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *

        FROM analysis_history

        WHERE id=?
        """,
        (report_id,)
    )

    report = cursor.fetchone()

    conn.close()

    return report