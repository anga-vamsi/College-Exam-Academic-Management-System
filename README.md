# College Exam & Academic Management System

A secure, role-based web application for managing college academic activities such as students, faculty, courses, subjects, examinations, marks, results, and attendance.

The system is built using **Python Flask and MySQL** and is deployed using **Render** with **Aiven MySQL** as the cloud database.

---

## 🚀 Live Application

**Live Demo:**  
https://college-exam-academic-management-system.onrender.com

> The application is deployed on Render and uses a cloud-hosted Aiven MySQL database.

---

## 📌 GitHub Repository

https://github.com/vamsi-bear/College-Exam-Academic-Management-System

---

## 📖 Project Overview

The **College Exam & Academic Management System** provides a centralized platform for managing academic information within a college.

The system supports multiple user roles with different permissions:

- **ADMIN**
- **PRINCIPAL**
- **FACULTY**
- **STUDENT**

Each role receives access only to the features appropriate for that role.

The application provides academic management functionality along with security features such as:

- Password hashing
- Role-based authorization
- CSRF protection
- Secure sessions
- Input validation
- Database protection
- Error handling

---

## ✨ Key Features

### 🔐 Authentication & Authorization

- Secure user login
- Password hashing using Werkzeug
- Role-based access control
- Session-based authentication
- Student account association
- Secure logout
- CSRF protection
- Protected administrative routes

### 👨‍🎓 Student Management

- View students
- Add students
- Edit student information
- Delete students
- Search students
- View student academic information
- Student-specific dashboard

### 👨‍🏫 Faculty Management

- Faculty records
- Department association
- Faculty profile management
- Role-based faculty access

### 📚 Academic Management

- Course management
- Subject management
- Department management
- Semester information
- Academic year information

### 📝 Examination Management

- Exam management
- Exam scheduling
- Subject-wise examination schedules
- Exam date and time
- Examination room information
- Marks management

### 📊 Academic Reports

The system provides:

- Student performance reports
- Student attendance reports
- Student result reports
- Subject-wise performance information
- Percentage calculation
- Grade calculation
- PASS / FAIL status

### 📅 Attendance Management

- Total classes
- Attended classes
- Attendance percentage
- Subject-wise attendance
- Student attendance reports

### 🛡️ Security

The application includes:

- Role-based authorization
- CSRF protection
- Password hashing
- Secure session cookies
- Input validation
- Email validation
- Phone validation
- Integer and decimal validation
- Protected database routes
- Custom `403`, `404`, and `500` error pages
- Environment-based configuration
- Database connection cleanup

---

## 👥 User Roles

| Role | Main Capabilities |
|------|-------------------|
| **ADMIN** | Manage students, faculty, courses, subjects, exams, results, attendance and reports |
| **PRINCIPAL** | Access academic information, reports and management-level views |
| **FACULTY** | Access academic information, subjects, results, attendance and student performance |
| **STUDENT** | Access personal dashboard, performance, attendance and results |

---

## 🛠️ Technology Stack

### Backend

- Python
- Flask
- MySQL Connector/Python
- Werkzeug
- Gunicorn

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates

### Database

- MySQL 8
- MySQL Views
- MySQL Stored Procedures

### Development

- Visual Studio Code
- Git
- GitHub
- Python Virtual Environment

### Deployment

- Render
- Aiven MySQL

---

## 🏗️ System Architecture

```text
                    ┌──────────────────────┐
                    │       Browser        │
                    │  HTML/CSS/JavaScript │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      Flask App       │
                    │       Python         │
                    ├──────────────────────┤
                    │ Authentication       │
                    │ Authorization        │
                    │ Validation           │
                    │ Business Logic       │
                    │ Reports              │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       MySQL          │
                    ├──────────────────────┤
                    │ Tables               │
                    │ Views                │
                    │ Stored Procedures    │
                    └──────────────────────┘