Update the EXISTING README.md of my College Exam & Academic Management System.

IMPORTANT:
- Modify README.md only.
- Do not create any new files.
- Do not modify Python, HTML, CSS, database, tests, or configuration files.
- Do not invent features, URLs, statistics, screenshots, credentials, or deployment information.
- Use only features that actually exist in the project.

Project:
College Exam & Academic Management System

Technology:
- Python
- Flask
- MySQL 8.0
- Jinja2 templates
- HTML5
- CSS3
- JavaScript
- pytest
- Git/GitHub

Document the following sections:

# College Exam & Academic Management System

Add a professional one-paragraph project description explaining that this is a web-based academic management system for managing students, faculty, courses, subjects, examinations, results, attendance, dashboards, and academic reports.

## Features

Include only implemented features such as:
- Student management
- Faculty management
- Course management
- Subject management
- Examination management
- Result management
- Attendance management
- Student performance reports
- Student attendance reports
- Academic reports
- Role-based access control
- Login and registration
- Profile
- CSRF protection
- Server-side validation
- Secure session configuration
- MySQL database integration
- Search functionality
- CRUD operations where implemented

## User Roles

Document the implemented roles:
- ADMIN
- PRINCIPAL
- FACULTY
- STUDENT

Explain the access model briefly without claiming permissions that are not implemented.

## Technology Stack

Create a clean table containing:
Technology | Purpose

Include Python, Flask, MySQL, HTML5, CSS3, JavaScript, Jinja2, pytest, Git, and GitHub.

## Project Structure

Show the important existing directories/files, for example:

College-Exam-Academic-System/
├── app.py
├── config.py
├── db.py
├── utils.py
├── database.sql
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .gitignore
├── static/
├── templates/
└── tests/

Do not invent files that do not exist.

## Database

Explain that MySQL 8.0 is used.

Mention the database name:
college_academic_system

Mention the major implemented entities:
Student
Faculty
Department
Course
Subject
Exam
Exam Schedule
Attendance
Marks
Result
Users

Mention that database connection settings are loaded from environment variables.

## Installation

Provide exact Windows setup instructions:

1. Clone:
git clone https://github.com/anga-vamsi/College-Exam-Academic-Management-System.git

2. Enter:
cd College-Exam-Academic-Management-System

3. Create virtual environment:
python -m venv venv

4. Activate:
venv\Scripts\activate

5. Install dependencies:
python -m pip install -r requirements.txt

6. Create a local .env file.

Use placeholders only:

SECRET_KEY=your-secret-key
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DATABASE=college_academic_system

Clearly state:
- Never commit .env.
- Never put real database passwords in config.py.
- The repository .gitignore excludes .env.

## Database Setup

Explain how to:
- Start MySQL 8.0.
- Create/select the college_academic_system database.
- Import database.sql.
- Verify the database connection.

Do not include any real password.

## Running the Application

Show:

python app.py

Then:

http://127.0.0.1:5000

## Testing

Document the actual latest test result:

60 passed, 2 warnings

Mention that the two warnings are deprecation warnings related to MySQL cursor stored procedure result handling and are not test failures.

Do not claim 100% coverage unless it exists in the project.

## Security

Document only implemented security features:
- Password hashing
- Role-based authorization
- CSRF protection
- Environment-based secrets
- HTTP-only session cookies
- SameSite session cookies
- Server-side input validation
- POST-based destructive operations where implemented

Do not claim encryption or security controls that are not actually implemented.

## UI

Mention that the application uses existing reusable CSS components for:
- Login
- Register
- Profile
- Logout
- Edit
- Delete
- Attendance
- Performance
- View Report
- Search
- Clear
- Back to Home
- Show/Hide

Mention smooth hover, active, focus, and responsive states where implemented.

## Testing Command

Include:

python -m pytest

## Repository

Add:

https://github.com/anga-vamsi/College-Exam-Academic-Management-System

## Author

Use:

Vamsi Anga

Do not add personal contact information unless it is already present in README.md.

Finish with a concise note that the project was developed for academic/educational purposes.

Make the README professional, clean, recruiter-friendly, and easy to scan.