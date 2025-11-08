"""
Betty Phipps

11/08/2025

Module 11: Build Role Based Access Control

Due Sunday September 9

explanation of file: Database initialization and seeding script.
"""

import os
import sqlite3
from pathlib import Path

from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash

from utils import encrypt_text, get_project_root


def ensure_fernet_key(project_root: Path) -> bytes:
    """
    Ensure a Fernet key is available either by environment variable or file.
    If neither source exists, generate a new key and persist it to key.key.
    """
    env_key = os.environ.get("FERNET_KEY")
    if env_key:
        return env_key.encode("utf-8")

    key_path = project_root / "key.key"
    if key_path.exists():
        key_bytes = key_path.read_bytes()
        os.environ["FERNET_KEY"] = key_bytes.decode("utf-8")
        return key_bytes

    key_bytes = Fernet.generate_key()
    key_path.write_bytes(key_bytes)
    os.chmod(key_path, 0o600)
    os.environ["FERNET_KEY"] = key_bytes.decode("utf-8")
    return key_bytes


def initialize_database(db_path: Path) -> None:
    """
    Create tables with the prescribed schema and seed initial records.
    """
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        # Create tables if they do not already exist.
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                security_level INTEGER NOT NULL,
                emp_id INTEGER,
                FOREIGN KEY (emp_id) REFERENCES Employees(id)
            );

            CREATE TABLE IF NOT EXISTS Employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                department TEXT,
                security_level INTEGER DEFAULT 3
            );

            CREATE TABLE IF NOT EXISTS EmpPayRaise (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                payraise_date_encrypted BLOB NOT NULL,
                raiseamt_encrypted BLOB NOT NULL,
                comments_encrypted BLOB,
                FOREIGN KEY (emp_id) REFERENCES Employees(id),
                FOREIGN KEY (user_id) REFERENCES Users(id)
            );
            """
        )

        conn.commit()

        # Seed employees and users together to maintain relationships.
        employees = [
            {
                "username": "admin1",
                "password": "AdminPass1",
                "full_name": "Alice Admin",
                "security_level": 1,
                "employee": {
                    "name": "Alice Admin",
                    "email": "alice.admin@example.com",
                    "department": "Executive",
                    "security_level": 1,
                },
            },
            {
                "username": "manager",
                "password": "Manager1",
                "full_name": "Bob Manager",
                "security_level": 2,
                "employee": {
                    "name": "Bob Manager",
                    "email": "bob.manager@example.com",
                    "department": "Operations",
                    "security_level": 2,
                },
            },
            {
                "username": "staff",
                "password": "Staff1",
                "full_name": "Cara Staff",
                "security_level": 3,
                "employee": {
                    "name": "Cara Staff",
                    "email": "cara.staff@example.com",
                    "department": "Support",
                    "security_level": 3,
                },
            },
        ]

        for entry in employees:
            # Insert employee if missing.
            emp = entry["employee"]
            cur = conn.execute(
                "SELECT id FROM Employees WHERE name = ? AND email = ?",
                (emp["name"], emp["email"]),
            )
            emp_row = cur.fetchone()
            if emp_row:
                emp_id = emp_row[0]
            else:
                cur = conn.execute(
                    """
                    INSERT INTO Employees (name, email, department, security_level)
                    VALUES (?, ?, ?, ?)
                    """,
                    (emp["name"], emp["email"], emp["department"], emp["security_level"]),
                )
                emp_id = cur.lastrowid

            # Insert user if missing.
            cur = conn.execute(
                "SELECT id FROM Users WHERE username = ?",
                (entry["username"],),
            )
            user_row = cur.fetchone()
            if user_row:
                user_id = user_row[0]
            else:
                password_hash = generate_password_hash(entry["password"])
                cur = conn.execute(
                    """
                    INSERT INTO Users (username, password_hash, full_name, security_level, emp_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        entry["username"],
                        password_hash,
                        entry["full_name"],
                        entry["security_level"],
                        emp_id,
                    ),
                )
                user_id = cur.lastrowid

            # Ensure the relationship is linked even if user existed earlier.
            conn.execute(
                "UPDATE Users SET emp_id = ? WHERE id = ?",
                (emp_id, user_id),
            )
            conn.commit()

        # Seed an example pay raise for the admin user if none exist.
        cur = conn.execute("SELECT id FROM Users WHERE username = ?", ("admin1",))
        admin_user_id = cur.fetchone()[0]
        cur = conn.execute("SELECT emp_id FROM Users WHERE id = ?", (admin_user_id,))
        admin_emp_id = cur.fetchone()[0]

        cur = conn.execute(
            "SELECT COUNT(*) FROM EmpPayRaise WHERE user_id = ?",
            (admin_user_id,),
        )
        has_raises = cur.fetchone()[0] > 0

        if not has_raises:
            conn.execute(
                """
                INSERT INTO EmpPayRaise (
                    emp_id,
                    user_id,
                    payraise_date_encrypted,
                    raiseamt_encrypted,
                    comments_encrypted
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    admin_emp_id,
                    admin_user_id,
                    encrypt_text("2025-01-01"),
                    encrypt_text("1250.00"),
                    encrypt_text("Annual merit increase"),
                ),
            )
            conn.commit()


def main() -> None:
    """
    Entry point for CLI execution.
    """
    project_root = get_project_root()
    ensure_fernet_key(project_root)
    db_path = project_root / "app.db"
    initialize_database(db_path)
    print("Database initialized and seeded successfully.")


if __name__ == "__main__":
    main()

