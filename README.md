# Secure Pay Raise Portal (Flask Application)

This project is a secure Flask-based web application that manages employee accounts and pay raises. The application uses encrypted data storage, role-based access control, and protected session management to demonstrate secure computing principles.

## 🔐 Key Features
- User login with password hashing and authentication
- Role-based authorization using `SecurityLevel` controls
- Encrypted storage of pay raise information using **cryptography.Fernet**
- Session tracking with `flask.session`
- Form validation and flash messaging for user feedback
- SQLite database backend for lightweight deployment

## 🧑‍💼 User Roles & Permissions

| SecurityLevel | Access Permissions |
|--------------|-------------------|
| **1** | Add Employee, Add Pay Raise, List Employees, Show My Pay Raises |
| **2** | List Pay Raises, List Employees, Add Pay Raise, Show My Pay Raises |
| **3** | Show My Pay Raises, Add Pay Raise |
| Not Logged In | Redirected to Login Page |

Unauthorized access attempts result in a "Page not found" message.

---

## 🗂 Project Structure

