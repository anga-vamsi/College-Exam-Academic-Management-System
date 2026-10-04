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

The College Exam & Academic Management System provides a centralized platform for managing academic information within a college.

The system supports multiple user roles with different permissions:

- **Admin**
- **Principal**
- **Faculty**
- **Student**

Each role receives access only to the features appropriate for that role.

The application provides academic management functionality along with security features such as password hashing, role-based authorization, CSRF protection, secure sessions, input validation, and error handling.

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
- Pass/Fail status

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
                    │      Python          │
                    ├──────────────────────┤
                    │ Authentication       │
                    │ Authorization        │
                    │ Validation            │
                    │ Business Logic       │
                    │ Reports              │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │        MySQL         │
                    │      Database        │
                    ├──────────────────────┤
                    │ Tables               │
                    │ Views                │
                    │ Stored Procedures    │
                    └──────────────────────┘
                    
                    
Production Architecture

GitHub
   │
   ▼
Render
   │
   │ Flask + Gunicorn
   ▼
Aiven MySQL
   │
   ▼
Academic Database
📂 Project Structure
College-Exam-Academic-System/
│
├── app.py
├── config.py
├── db.py
├── utils.py
├── requirements.txt
├── pytest.ini
├── README.md
├── .gitignore
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── students.html
│   ├── faculty.html
│   ├── courses.html
│   ├── subjects.html
│   ├── exams.html
│   ├── results.html
│   ├── attendance.html
│   ├── student_performance.html
│   └── ...
│
├── static/
│   └── css/
│       ├── auth.css
│       ├── components.css
│       ├── navbar.css
│       └── report-actions.css
│
└── tests/
    └── test_app.py
🗄️ Database Design

The main database is:

college_academic_system
Main Tables
users
student
faculty
department
course
subject
exam
exam_schedule
marks
result
attendance
Database Views
student_attendance_view
student_performance_view
student_result_view
Stored Procedures
GetStudentAttendance
GetStudentPerformance
GetStudentResult

The stored procedures are used to generate structured academic reports.

📊 Performance Report

The Student Performance Report provides:

Field	Description
Exam	Examination name
Subject	Subject code and subject name
Total Marks	Marks obtained / maximum marks
Percentage	Calculated percentage
Grade	Calculated academic grade
Status	PASS / FAIL

Example:

Exam       Subject                         Marks     Percentage   Grade   Status
--------------------------------------------------------------------------------
Mid Term   CS301 - Database Management     44/50      88%          A      PASS
Mid Term   CS302 - Operating Systems       43/50      86%          A      PASS
Mid Term   CS303 - Computer Networks       45/50      90%          A+     PASS
📅 Attendance Report

The attendance report includes:

Student
Roll Number
Subject Code
Subject Name
Total Classes
Attended Classes
Attendance Percentage

Attendance percentage is calculated from the total and attended class counts.

📈 Result Management

The result module provides:

Total marks
Percentage
Grade
Result status
Examination
Semester
Academic year

The system calculates academic status based on the student's marks.

🔒 Security Implementation
Password Security

Passwords are stored using secure password hashing rather than plain text.

Role-Based Access Control

Protected routes use role validation to ensure users can access only authorized functionality.

Example roles:

ADMIN
PRINCIPAL
FACULTY
STUDENT
CSRF Protection

POST requests are protected using CSRF tokens stored in the user's session.

Session Security

The application uses secure session configuration including:

HttpOnly
SameSite=Lax
Secure Cookie support
Input Validation

The application validates:

Text fields
Email addresses
Phone numbers
Integer values
Decimal values
Dates
Error Handling

Custom error pages are implemented for:

403 Forbidden
404 Not Found
500 Internal Server Error
⚙️ Local Installation
1. Clone the repository
git clone https://github.com/vamsi-bear/College-Exam-Academic-Management-System.git

Move into the project:

cd College-Exam-Academic-System
2. Create a virtual environment

Windows:

python -m venv venv

Activate it:

venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
🔑 Environment Variables

Create a .env file in the project root.

Example:

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=college_academic_system

SECRET_KEY=your_secret_key

SESSION_COOKIE_SECURE=0

For production, use the appropriate cloud database credentials and:

SESSION_COOKIE_SECURE=1

Never commit .env or database passwords to GitHub.

🗃️ Database Setup

Make sure MySQL is installed and running.

Create the database:

CREATE DATABASE college_academic_system;

Then import the database schema/data using the appropriate SQL file.

Example:

mysql -u root -p college_academic_system < college_academic_system_clean.sql
▶️ Run the Application

Start the Flask application:

python app.py

Open:

http://127.0.0.1:5000
🧪 Running Tests

The project uses pytest.

Run:

pytest

The test suite verifies important application functionality including routes, authentication, authorization and application behavior.

☁️ Deployment
Render

The Flask application is deployed on:

Render

Production start command:

gunicorn app:app
Aiven

The production MySQL database is hosted using:

Aiven MySQL

The Flask application connects to the cloud database through environment variables.

🔄 Deployment Workflow
Developer
    │
    ▼
VS Code
    │
    ▼
Git
    │
    ▼
GitHub
    │
    ▼
Render
    │
    ▼
Flask + Gunicorn
    │
    ▼
Aiven MySQL

Future changes can be committed and pushed using:

git add .
git commit -m "Your commit message"
git push origin main

Render can then deploy the updated main branch.

🌐 Project Links
GitHub

https://github.com/vamsi-bear/College-Exam-Academic-Management-System

Live Application

https://college-exam-academic-management-system.onrender.com

🎯 Project Objectives

The main objectives of the project are:

Centralize academic information
Reduce manual academic record management
Provide role-based access
Simplify student performance tracking
Manage attendance efficiently
Provide examination and result management
Generate academic reports
Improve security of academic data
Provide a deployable cloud-based solution
🚀 Future Enhancements

Possible future improvements include:

Email notifications
Student result PDF generation
Faculty-specific dashboards
Advanced analytics
Attendance alerts
Automated report generation
REST API integration
Two-factor authentication
Audit logging
Cloud monitoring
Mobile application
🧑‍💻 Author

Vamsi Anga

Computer Science & Engineering Student

GitHub:

https://github.com/vamsi-bear

📄 License

This project is intended for academic, educational, and portfolio purposes.


### Save it

After replacing `README.md`, run:

```bat
git status