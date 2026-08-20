"""
database.py
------------
Lightweight SQLite persistence layer (stdlib sqlite3, no ORM needed
for an MVP this size). Handles student profiles and the internship
application tracker.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "platform.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    degree TEXT,
    location TEXT,
    interests TEXT,
    experience_level TEXT DEFAULT 'none',
    skills_text TEXT,
    cv_text TEXT
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    internship_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Saved',
    applied_date TEXT,
    UNIQUE(student_id, internship_id)
);
"""


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def load_internships():
    path = os.path.join(os.path.dirname(__file__), "data", "internships.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_internship(internship_id):
    for i in load_internships():
        if i["id"] == int(internship_id):
            return i
    return None


# ---------------- Student profile ----------------

def create_or_update_student(student_id, data: dict):
    conn = get_db()
    if student_id:
        conn.execute(
            """UPDATE students SET name=?, degree=?, location=?, interests=?,
               experience_level=?, skills_text=?, cv_text=? WHERE id=?""",
            (data["name"], data["degree"], data["location"], data["interests"],
             data["experience_level"], data["skills_text"], data["cv_text"], student_id),
        )
        conn.commit()
        conn.close()
        return student_id
    else:
        cur = conn.execute(
            """INSERT INTO students (name, degree, location, interests, experience_level,
               skills_text, cv_text) VALUES (?,?,?,?,?,?,?)""",
            (data["name"], data["degree"], data["location"], data["interests"],
             data["experience_level"], data["skills_text"], data["cv_text"]),
        )
        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id


def get_student(student_id):
    if not student_id:
        return None
    conn = get_db()
    row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ---------------- Application tracker ----------------

def upsert_application(student_id, internship_id, status, applied_date=None):
    conn = get_db()
    conn.execute(
        """INSERT INTO applications (student_id, internship_id, status, applied_date)
           VALUES (?,?,?,?)
           ON CONFLICT(student_id, internship_id)
           DO UPDATE SET status=excluded.status,
                         applied_date=COALESCE(excluded.applied_date, applications.applied_date)""",
        (student_id, internship_id, status, applied_date),
    )
    conn.commit()
    conn.close()


def get_applications(student_id):
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM applications WHERE student_id=? ORDER BY id DESC", (student_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_application_status(student_id, internship_id):
    conn = get_db()
    row = conn.execute(
        "SELECT status FROM applications WHERE student_id=? AND internship_id=?",
        (student_id, internship_id),
    ).fetchone()
    conn.close()
    return row["status"] if row else None
