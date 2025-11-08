"""
Betty Phipps

11/08/2025

Module 11: Build Role Based Access Control

Due Sunday September 9

explanation of file: SQLite data helpers with Fernet encryption support.
"""

import sqlite3
from typing import Any, Dict, List, Optional

from utils import decrypt_text, encrypt_text, get_project_root


def _db_path() -> str:
    """
    Construct the absolute path to the SQLite database file.
    """
    return str(get_project_root() / "app.db")


def _get_connection() -> sqlite3.Connection:
    """
    Establish a new SQLite connection using row factory for dict-like access.
    """
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    """
    Fetch a single user row by username.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash, full_name, security_level, emp_id FROM Users WHERE username = ?",
            (username,),
        )
        return cur.fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    """
    Fetch a single user row by primary key.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "SELECT id, username, password_hash, full_name, security_level, emp_id FROM Users WHERE id = ?",
            (user_id,),
        )
        return cur.fetchone()


def create_user(username: str, password_hash: str, full_name: str, security_level: int) -> int:
    """
    Insert a new user into the Users table.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO Users (username, password_hash, full_name, security_level)
            VALUES (?, ?, ?, ?)
            """,
            (username, password_hash, full_name, security_level),
        )
        conn.commit()
        return cur.lastrowid


def get_employees() -> List[Dict[str, Any]]:
    """
    Retrieve all employees.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "SELECT id, name, email, department, security_level FROM Employees ORDER BY name"
        )
        return [dict(row) for row in cur.fetchall()]


def get_emp_by_id(emp_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a single employee by ID.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            "SELECT id, name, email, department, security_level FROM Employees WHERE id = ?",
            (emp_id,),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def create_employee(name: str, email: str, department: str, security_level: int) -> int:
    """
    Insert a new employee record.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO Employees (name, email, department, security_level)
            VALUES (?, ?, ?, ?)
            """,
            (name, email, department, security_level),
        )
        conn.commit()
        return cur.lastrowid


def create_payraise(user_id: int, emp_id: int, date_str: str, raise_amt: float, comments: Optional[str] = None) -> int:
    """
    Insert a new pay raise record with encrypted fields.
    Comments are optional and encrypted when provided to keep sensitive notes private.
    """
    # Prepare encrypted values as bytes before storing.
    encrypted_date = encrypt_text(date_str.strip())
    encrypted_amt = encrypt_text(f"{float(raise_amt):.2f}")
    encrypted_comments = encrypt_text(comments.strip()) if comments else None

    with _get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO EmpPayRaise (
                emp_id, user_id, payraise_date_encrypted, raiseamt_encrypted, comments_encrypted
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (emp_id, user_id, encrypted_date, encrypted_amt, encrypted_comments),
        )
        conn.commit()
        return cur.lastrowid


def get_payraises_for_user(user_id: int) -> List[Dict[str, Any]]:
    """
    Retrieve decrypted pay raise records for a specific user.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            """
            SELECT e.name AS employee_name,
                   pr.payraise_date_encrypted,
                   pr.raiseamt_encrypted,
                   pr.comments_encrypted
            FROM EmpPayRaise pr
            JOIN Employees e ON e.id = pr.emp_id
            WHERE pr.user_id = ?
            ORDER BY pr.id DESC
            """,
            (user_id,),
        )
        results = []
        for row in cur.fetchall():
            decrypted_row = {
                "employee_name": row["employee_name"],
                "payraise_date": decrypt_text(row["payraise_date_encrypted"]),
                "raise_amount": decrypt_text(row["raiseamt_encrypted"]),
                "comments": decrypt_text(row["comments_encrypted"])
                if row["comments_encrypted"]
                else "",
            }
            results.append(decrypted_row)
        return results


def get_all_payraises() -> List[Dict[str, Any]]:
    """
    Retrieve all pay raises with decrypted values for authorized viewing.
    """
    with _get_connection() as conn:
        cur = conn.execute(
            """
            SELECT pr.id,
                   e.name AS employee_name,
                   pr.user_id,
                   pr.payraise_date_encrypted,
                   pr.raiseamt_encrypted,
                   pr.comments_encrypted
            FROM EmpPayRaise pr
            JOIN Employees e ON e.id = pr.emp_id
            ORDER BY pr.id DESC
            """
        )
        results = []
        for row in cur.fetchall():
            decrypted_row = {
                "id": row["id"],
                "employee_name": row["employee_name"],
                "user_id": row["user_id"],
                "payraise_date": decrypt_text(row["payraise_date_encrypted"]),
                "raise_amount": decrypt_text(row["raiseamt_encrypted"]),
                "comments": decrypt_text(row["comments_encrypted"])
                if row["comments_encrypted"]
                else "",
            }
            results.append(decrypted_row)
        return results

