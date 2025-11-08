"""
Betty Phipps

11/08/2025

Module 11: Build Role Based Access Control

Due Sunday September 9

explanation of file: Form dataclasses providing user input validation.
"""

from dataclasses import dataclass, field
from typing import Mapping, Optional

from utils import is_positive_number, is_valid_date


@dataclass
class LoginForm:
    """
    Simple container for login form data.
    """

    username: str = ""
    password: str = ""
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, str]) -> "LoginForm":
        """
        Build a LoginForm from request.form-like mapping.
        """
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()
        errors: list[str] = []
        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")
        return cls(username=username, password=password, errors=errors)


@dataclass
class PayRaiseForm:
    """
    Validate the add pay raise submission.
    """

    payraise_date: str = ""
    raise_amount: str = ""
    comments: str = ""
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, str]) -> "PayRaiseForm":
        """
        Construct and validate the pay raise form input.
        """
        payraise_date = (data.get("payraise_date") or "").strip()
        raise_amount = (data.get("raise_amount") or "").strip()
        comments = (data.get("comments") or "").strip()
        errors: list[str] = []

        if not is_valid_date(payraise_date):
            errors.append("PayRaiseDate must be a valid date (YYYY-MM-DD).")
        if not is_positive_number(raise_amount):
            errors.append("RaiseAmt must be a positive number.")

        return cls(
            payraise_date=payraise_date,
            raise_amount=raise_amount,
            comments=comments,
            errors=errors,
        )


@dataclass
class EmployeeForm:
    """
    Validate the add employee form submission.
    """

    name: str = ""
    email: str = ""
    department: str = ""
    security_level: Optional[int] = None
    errors: list[str] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, data: Mapping[str, str]) -> "EmployeeForm":
        """
        Construct and validate the employee form input.
        """
        name = (data.get("name") or "").strip()
        email = (data.get("email") or "").strip()
        department = (data.get("department") or "").strip()
        security_level_raw = (data.get("security_level") or "").strip()
        errors: list[str] = []

        if not name:
            errors.append("Employee name is required.")

        security_level: Optional[int] = None
        if security_level_raw:
            try:
                security_level = int(security_level_raw)
                if security_level not in (1, 2, 3):
                    errors.append("Security level must be 1, 2, or 3.")
            except ValueError:
                errors.append("Security level must be a number.")
        else:
            errors.append("Security level is required.")

        if not department:
            errors.append("Department is required.")

        return cls(
            name=name,
            email=email,
            department=department,
            security_level=security_level,
            errors=errors,
        )

