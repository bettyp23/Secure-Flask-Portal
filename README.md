# Secure Pay Raise Flask Portal

This project delivers a secure Flask web application that demonstrates encrypted data storage, access control by security level, session management, input validation, and flash messaging.

## Features

- Credentialed login with session storage using `flask.session`.
- Role-based navigation and authorization enforced in routes and templates.
- Pay raise data encrypted using `cryptography.Fernet`.
- Flash messaging for feedback on authentication, validation, and authorization events.
- SQLite database seeded with sample users, employees, and encrypted pay raise data.

## Quick Start

```bash
python3 -m venv venv
source venv/bin/activate   # On Windows use venv\Scripts\activate
pip install -r requirements.txt
python init_db.py          # Generates key.key (if needed) and seeds app.db
python app.py              # Or: flask --app app run
```

Visit http://127.0.0.1:5000 in your browser.

## Environment Variables

- `FLASK_SECRET`: Secret key for Flask sessions. Defaults to `dev-secret-please-change`. Set to a strong random string for production.
- `FERNET_KEY`: Optional base64 Fernet key. If unset, `init_db.py` creates `key.key` with restricted permissions (0600) and loads it automatically.

Example:

```bash
export FLASK_SECRET="replace-with-strong-secret"
export FERNET_KEY="$(python -c 'from cryptography.fernet import Fernet;print(Fernet.generate_key().decode())')"
```

## Seeded Accounts

| Username | Password   | Security Level | Full Name    |
|----------|------------|----------------|--------------|
| admin1   | AdminPass1 | 1              | Alice Admin  |
| manager  | Manager1   | 2              | Bob Manager  |
| staff    | Staff1     | 3              | Cara Staff   |

## Testing Scenarios

1. Invalid login attempts stay on the login page and flash `invalid username and/or password!`.
2. Admin (security level 1) can view and add employees, add pay raises, and view personal raises.
3. Manager (level 2) can list employees and all pay raises.
4. Staff (level 3) can only view personal raises and add new ones.
5. Unauthorized route access flashes `Page not found` and renders the error page with HTTP 404.

## Project Structure

```
Secure-Flask-Portal/
├─ app.py
├─ forms.py
├─ init_db.py
├─ models.py
├─ utils.py
├─ requirements.txt
├─ key.key             # created by init_db.py if needed
├─ app.db              # created by init_db.py
├─ templates/
│  ├─ base.html
│  ├─ login.html
│  ├─ home.html
│  ├─ show_payraises.html
│  ├─ add_payraise.html
│  ├─ add_employee.html
│  ├─ list_employees.html
│  ├─ list_payraises.html
│  ├─ result.html
│  └─ error.html
└─ static/
```
