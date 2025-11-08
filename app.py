"""
Betty Phipps

11/08/2025

Module 11: Build Role Based Access Control

Due Sunday September 9

explanation of file: Flask web application entry point enforcing RBAC.
"""

import os
from functools import wraps
from typing import Callable, Optional

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from forms import EmployeeForm, LoginForm, PayRaiseForm
from models import (
    create_employee,
    create_payraise,
    get_all_payraises,
    get_employees,
    get_payraises_for_user,
    get_user_by_username,
)

# Initialize Flask application.
app = Flask(__name__)

# Use os.environ explicitly per assignment requirement.
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-please-change")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_PERMANENT"] = False


def login_required(view: Callable) -> Callable:
    """
    Decorator enforcing that a valid session exists before proceeding.
    """

    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def requires_security_level(min_level: int) -> Callable:
    """
    Decorator enforcing that the logged-in user meets the minimum security level.
    """

    def decorator(view: Callable) -> Callable:
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            security_level: Optional[int] = session.get("security_level")
            if security_level is None or security_level < min_level:
                flash("Page not found")
                return render_template("error.html"), 404
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    """
    Display the login form and authenticate users.
    """
    if "user_id" in session:
        return redirect(url_for("home"))

    form = LoginForm.from_mapping(request.form if request.method == "POST" else {})

    if request.method == "POST":
        if form.errors:
            for message in form.errors:
                flash(message)
            return render_template("login.html", form=form)

        user_row = get_user_by_username(form.username)
        if user_row and check_password_hash(user_row["password_hash"], form.password):
            session.clear()
            session["user_id"] = user_row["id"]
            session["username"] = user_row["username"]
            session["full_name"] = user_row["full_name"]
            session["security_level"] = user_row["security_level"]
            session["emp_id"] = user_row["emp_id"]
            flash("Logged in successfully.")
            return redirect(url_for("home"))

        flash("invalid username and/or password!")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """
    Clear session and return to login page.
    """
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/home")
@login_required
def home():
    """
    Show the home dashboard with links conditioned on security level.
    """
    return render_template("home.html")


@app.route("/show_payraises")
@login_required
def show_payraises():
    """
    Display pay raises for the logged-in user with decrypted values.
    """
    user_id = session["user_id"]
    raises = get_payraises_for_user(user_id)

    # Format amounts for display while preserving encrypted storage.
    for entry in raises:
        try:
            amount = float(entry["raise_amount"])
            entry["raise_amount_display"] = f"${amount:,.2f}"
        except (TypeError, ValueError):
            entry["raise_amount_display"] = entry["raise_amount"]

    return render_template("show_payraises.html", raises=raises)


@app.route("/add_payraise", methods=["GET", "POST"])
@login_required
def add_payraise():
    """
    Allow any authenticated user to add a pay raise for themselves.
    """
    form = PayRaiseForm.from_mapping(request.form if request.method == "POST" else {})

    if request.method == "POST":
        if form.errors:
            for message in form.errors:
                flash(message)
            flash("Record not added due to input errors.")
            return redirect(url_for("result"))

        emp_id = session.get("emp_id")
        if emp_id is None:
            flash("Page not found")
            return render_template("error.html"), 404

        create_payraise(
            user_id=session["user_id"],
            emp_id=emp_id,
            date_str=form.payraise_date,
            raise_amt=float(form.raise_amount),
            comments=form.comments if form.comments else None,
        )
        flash("Record added")
        return redirect(url_for("result"))

    return render_template("add_payraise.html", form=form)


@app.route("/add_employee", methods=["GET", "POST"])
@login_required
@requires_security_level(1)
def add_employee():
    """
    Allow administrators to create new employee records.
    """
    form = EmployeeForm.from_mapping(request.form if request.method == "POST" else {})

    if request.method == "POST":
        if form.errors:
            for message in form.errors:
                flash(message)
            flash("Employee not added due to input errors.")
            return redirect(url_for("result"))

        create_employee(
            name=form.name,
            email=form.email,
            department=form.department,
            security_level=form.security_level or 3,
        )
        flash("Employee added successfully.")
        return redirect(url_for("result"))

    return render_template("add_employee.html", form=form)


@app.route("/list_employees")
@login_required
@requires_security_level(1)
def list_employees():
    """
    Display the list of employees to authorized users (security levels 1 and 2).
    """
    if session.get("security_level") not in (1, 2):
        flash("Page not found")
        return render_template("error.html"), 404

    employees = get_employees()
    return render_template("list_employees.html", employees=employees)


@app.route("/list_payraises")
@login_required
@requires_security_level(2)
def list_payraises():
    """
    Display all pay raises to authorized users (security level >= 2).
    """
    if session.get("security_level") != 2:
        flash("Page not found")
        return render_template("error.html"), 404

    payraises = get_all_payraises()
    for entry in payraises:
        try:
            amount = float(entry["raise_amount"])
            entry["raise_amount_display"] = f"${amount:,.2f}"
        except (TypeError, ValueError):
            entry["raise_amount_display"] = entry["raise_amount"]
    return render_template("list_payraises.html", payraises=payraises)


@app.route("/result")
@login_required
def result():
    """
    Generic result page that shows flashed messages.
    """
    return render_template("result.html")


@app.route("/error")
def error():
    """
    Render a user-friendly 404-like page.
    """
    return render_template("error.html"), 404


@app.errorhandler(404)
def page_not_found(error):  # type: ignore[override]
    """
    Provide consistent messaging for unknown routes.
    """
    flash("Page not found")
    return render_template("error.html"), 404


if __name__ == "__main__":
    # Allow direct execution for local development convenience.
    app.run(debug=True)

