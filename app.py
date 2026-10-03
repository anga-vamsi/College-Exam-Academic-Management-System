from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
import os
import secrets
import hmac
import re
from db import get_db_connection
from datetime import datetime
from config import Config
from utils import login_required, role_required
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

app.config["SECRET_KEY"] = Config.SECRET_KEY

# =========================================================
# Secure Session Cookie Configuration
# =========================================================
# HttpOnly prevents client-side JavaScript from reading the session cookie.
# SameSite=Lax provides protection against common cross-site requests.
# Secure is enabled in production by setting SESSION_COOKIE_SECURE=1.

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "0") == "1"
)
# =========================================================
# CSRF Protection
# =========================================================

def generate_csrf_token():
    if "_csrf_token" not in session:
        session["_csrf_token"] = secrets.token_urlsafe(32)

    return session["_csrf_token"]


@app.context_processor
def inject_csrf_token():
    return {
        "csrf_token": generate_csrf_token
    }


@app.before_request
def validate_csrf_token():

    # CSRF protection is skipped only for automated tests.
    # All real application POST requests are still validated.
    if request.method != "POST" or app.config.get("TESTING"):
        return

    token = session.get("_csrf_token")
    form_token = request.form.get("_csrf_token")

    if not token or not form_token:
        abort(403)

    if not hmac.compare_digest(token, form_token):
        abort(403)


# =========================================================
# Server-Side Input Validation
# =========================================================

def clean_text(value, field_name, max_length, required=True):
    value = (value or "").strip()

    if required and not value:
        raise ValueError(f"{field_name} is required.")

    if len(value) > max_length:
        raise ValueError(
            f"{field_name} must be {max_length} characters or fewer."
        )

    return value


def parse_int(value, field_name, minimum=None, maximum=None, required=True):
    value = (value or "").strip()

    if not value:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None

    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid integer.")

    if minimum is not None and number < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")

    if maximum is not None and number > maximum:
        raise ValueError(f"{field_name} must be at most {maximum}.")

    return number


def parse_float(value, field_name, minimum=None, maximum=None):
    value = (value or "").strip()

    if not value:
        raise ValueError(f"{field_name} is required.")

    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field_name} must be a valid number.")

    if minimum is not None and number < minimum:
        raise ValueError(f"{field_name} must be at least {minimum}.")

    if maximum is not None and number > maximum:
        raise ValueError(f"{field_name} must be at most {maximum}.")

    return number


def validate_email(value):
    value = (value or "").strip()

    if not value:
        return ""

    if len(value) > 100:
        raise ValueError("Email must be 100 characters or fewer.")

    pattern = r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    pattern += r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    pattern += r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"

    if not re.fullmatch(pattern, value):
        raise ValueError("Please enter a valid email address.")

    return value


def validate_phone(value):
    value = (value or "").strip()

    if not value:
        return ""

    if not re.fullmatch(r"\+?[0-9]{7,15}", value):
        raise ValueError(
            "Phone must contain 7 to 15 digits and may start with +."
        )

    return value


def validate_date(value, field_name):
    value = (value or "").strip()

    if not value:
        return ""

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"{field_name} must be a valid date.")

    return value


def validate_time(value, field_name):
    value = (value or "").strip()

    if not value:
        raise ValueError(f"{field_name} is required.")

    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            datetime.strptime(value, fmt)
            return value
        except ValueError:
            continue

    raise ValueError(f"{field_name} must be a valid time.")


# =========================================================
# Context Processor
# =========================================================

@app.context_processor
def inject_current_date():
    return {
        "current_date": datetime.now().strftime("%d-%m-%Y %H:%M")
    }


# =========================================================
# Dashboard
# =========================================================

@app.route("/")
@login_required
def home():

    role = session.get("role")

    # Student → Student Dashboard
    if role == "STUDENT":
        student_id = session.get("student_id")

        if student_id:
            return redirect(
                url_for("student_dashboard", student_id=student_id)
            )

        flash("No student profile is linked to this account.", "error")
        return redirect(url_for("login"))

    # Admin / Principal / Faculty → Academic Dashboard
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM student")
    students = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM faculty")
    faculty = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM course")
    courses = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM subject")
    subjects = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM exam")
    exams = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM result")
    results = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) AS total FROM attendance")
    attendance = cursor.fetchone()["total"]

    cursor.close()
    connection.close()

    return render_template(
        "home.html",
        students=students,
        faculty=faculty,
        courses=courses,
        subjects=subjects,
        exams=exams,
        results=results,
        attendance=attendance
    )


# =========================================================
# Test Database
# =========================================================

@app.route("/test-db")
@role_required("ADMIN")
def test_db():

    connection = get_db_connection()

    if connection.is_connected():
        connection.close()
        return "Database connected successfully"

    return "Database connection failed"


# =========================================================
# Students
# =========================================================

@app.route("/students", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL")
def students():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            roll_no = clean_text(request.form.get("roll_no"), "Roll number", 30)
            name = clean_text(request.form.get("name"), "Name", 100)
            dob = validate_date(request.form.get("dob"), "Date of birth")
            gender = clean_text(request.form.get("gender"), "Gender", 20)

            if gender not in {"Male", "Female", "Other"}:
                raise ValueError("Gender must be Male, Female, or Other.")

            email = validate_email(request.form.get("email"))
            phone = validate_phone(request.form.get("phone"))
            course_id = parse_int(
                request.form.get("course_id"),
                "Course",
                minimum=1
            )
            admission_year = parse_int(
                request.form.get("admission_year"),
                "Admission year",
                minimum=2000,
                maximum=2100,
                required=False
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("students"))

        query = """
            INSERT INTO student
            (
                roll_no,
                name,
                dob,
                gender,
                email,
                phone,
                course_id,
                admission_year
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            roll_no,
            name,
            dob,
            gender,
            email,
            phone,
            course_id,
            admission_year
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error registering student: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("students"))

    cursor.execute("""
        SELECT
            course_id,
            course_name
        FROM course
        ORDER BY course_name
    """)

    courses = cursor.fetchall()

    search = request.args.get("search", "").strip()

    cursor.execute("""
        SELECT
            s.student_id,
            s.roll_no,
            s.name,
            s.email,
            s.phone,
            c.course_name,
            s.admission_year
        FROM student s
        JOIN course c
            ON s.course_id = c.course_id
        WHERE s.name LIKE %s
           OR s.roll_no LIKE %s
           OR s.email LIKE %s
        ORDER BY s.roll_no
    """, (
        "%" + search + "%",
        "%" + search + "%",
        "%" + search + "%"
    ))

    students_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "students.html",
        students=students_data,
        courses=courses,
        search=search
    )


# =========================================================
# Delete Student
# =========================================================

@app.route("/students/delete/<int:student_id>", methods=["POST"])
@role_required("ADMIN")
def delete_student(student_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM student
            WHERE student_id = %s
        """, (student_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting student: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("students"))


# =========================================================
# Edit Student
# =========================================================

@app.route("/students/edit/<int:student_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_student(student_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            roll_no = clean_text(request.form.get("roll_no"), "Roll number", 30)
            name = clean_text(request.form.get("name"), "Name", 100)
            dob = validate_date(request.form.get("dob"), "Date of birth")
            gender = clean_text(request.form.get("gender"), "Gender", 20)

            if gender not in {"Male", "Female", "Other"}:
                raise ValueError("Gender must be Male, Female, or Other.")

            email = validate_email(request.form.get("email"))
            phone = validate_phone(request.form.get("phone"))
            course_id = parse_int(
                request.form.get("course_id"),
                "Course",
                minimum=1
            )
            admission_year = parse_int(
                request.form.get("admission_year"),
                "Admission year",
                minimum=2000,
                maximum=2100,
                required=False
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_student", student_id=student_id))

        query = """
            UPDATE student
            SET
                roll_no = %s,
                name = %s,
                dob = %s,
                gender = %s,
                email = %s,
                phone = %s,
                course_id = %s,
                admission_year = %s
            WHERE student_id = %s
        """

        values = (
            roll_no,
            name,
            dob,
            gender,
            email,
            phone,
            course_id,
            admission_year,
            student_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating student: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("students"))

    cursor.execute("""
        SELECT
            student_id,
            roll_no,
            name,
            dob,
            gender,
            email,
            phone,
            course_id,
            admission_year
        FROM student
        WHERE student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    cursor.execute("""
        SELECT
            course_id,
            course_name
        FROM course
        ORDER BY course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_student.html",
        student=student,
        courses=courses
    )


# =========================================================
# Faculty
# =========================================================

@app.route("/faculty", methods=["GET", "POST"])
@role_required("ADMIN")
def faculty():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            name = clean_text(request.form.get("name"), "Name", 100)
            email = validate_email(request.form.get("email"))
            phone = validate_phone(request.form.get("phone"))
            dept_id = parse_int(
                request.form.get("dept_id"),
                "Department",
                minimum=1
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("faculty"))

        query = """
            INSERT INTO faculty
            (
                name,
                email,
                phone,
                dept_id
            )
            VALUES (%s, %s, %s, %s)
        """

        values = (
            name,
            email,
            phone,
            dept_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error registering faculty: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("faculty"))

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_name
    """)

    departments = cursor.fetchall()

    cursor.execute("""
        SELECT
            f.faculty_id,
            f.name,
            f.email,
            f.phone,
            d.dept_name
        FROM faculty f
        JOIN department d
            ON f.dept_id = d.dept_id
        ORDER BY f.name
    """)

    faculty_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "faculty.html",
        faculty=faculty_data,
        departments=departments
    )


# =========================================================
# Edit Faculty
# =========================================================

@app.route("/faculty/edit/<int:faculty_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_faculty(faculty_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            name = clean_text(request.form.get("name"), "Name", 100)
            email = validate_email(request.form.get("email"))
            phone = validate_phone(request.form.get("phone"))
            dept_id = parse_int(
                request.form.get("dept_id"),
                "Department",
                minimum=1
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_faculty", faculty_id=faculty_id))

        query = """
            UPDATE faculty
            SET
                name = %s,
                email = %s,
                phone = %s,
                dept_id = %s
            WHERE faculty_id = %s
        """

        values = (
            name,
            email,
            phone,
            dept_id,
            faculty_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating faculty: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("faculty"))

    cursor.execute("""
        SELECT
            faculty_id,
            name,
            email,
            phone,
            dept_id
        FROM faculty
        WHERE faculty_id = %s
    """, (faculty_id,))

    faculty_member = cursor.fetchone()

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_faculty.html",
        faculty=faculty_member,
        departments=departments
    )


# =========================================================
# Delete Faculty
# =========================================================

@app.route("/faculty/delete/<int:faculty_id>", methods=["POST"])
@role_required("ADMIN")
def delete_faculty(faculty_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM faculty
            WHERE faculty_id = %s
        """, (faculty_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting faculty: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("faculty"))


# =========================================================
# Courses
# =========================================================

@app.route("/courses", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL")
def courses():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            course_name = clean_text(
                request.form.get("course_name"),
                "Course name",
                100
            )
            duration = parse_int(
                request.form.get("duration"),
                "Duration",
                minimum=1,
                maximum=10
            )
            dept_id = parse_int(
                request.form.get("dept_id"),
                "Department",
                minimum=1
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("courses"))

        query = """
            INSERT INTO course
            (
                course_name,
                duration,
                dept_id
            )
            VALUES (%s, %s, %s)
        """

        values = (
            course_name,
            duration,
            dept_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error adding course: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("courses"))

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_name
    """)

    departments = cursor.fetchall()

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            c.duration,
            d.dept_name
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        ORDER BY c.course_name
    """)

    courses_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "courses.html",
        courses=courses_data,
        departments=departments
    )


# =========================================================
# Edit Course
# =========================================================

@app.route("/courses/edit/<int:course_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_course(course_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            course_name = clean_text(
                request.form.get("course_name"),
                "Course name",
                100
            )
            duration = parse_int(
                request.form.get("duration"),
                "Duration",
                minimum=1,
                maximum=10
            )
            dept_id = parse_int(
                request.form.get("dept_id"),
                "Department",
                minimum=1
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_course", course_id=course_id))

        query = """
            UPDATE course
            SET
                course_name = %s,
                duration = %s,
                dept_id = %s
            WHERE course_id = %s
        """

        values = (
            course_name,
            duration,
            dept_id,
            course_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating course: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("courses"))

    cursor.execute("""
        SELECT
            course_id,
            course_name,
            duration,
            dept_id
        FROM course
        WHERE course_id = %s
    """, (course_id,))

    course = cursor.fetchone()

    cursor.execute("""
        SELECT
            dept_id,
            dept_name
        FROM department
        ORDER BY dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_course.html",
        course=course,
        departments=departments
    )


# =========================================================
# Delete Course
# =========================================================

@app.route("/courses/delete/<int:course_id>", methods=["POST"])
@role_required("ADMIN")
def delete_course(course_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM course
            WHERE course_id = %s
        """, (course_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting course: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("courses"))


# =========================================================
# Subjects
# =========================================================

@app.route("/subjects", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL", "FACULTY")
def subjects():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            subject_code = clean_text(
                request.form.get("subject_code"),
                "Subject code",
                20
            )
            subject_name = clean_text(
                request.form.get("subject_name"),
                "Subject name",
                100
            )
            credits = parse_int(
                request.form.get("credits"),
                "Credits",
                minimum=1,
                maximum=10
            )
            semester = parse_int(
                request.form.get("semester"),
                "Semester",
                minimum=1,
                maximum=8
            )
            course_id = parse_int(
                request.form.get("course_id"),
                "Course",
                minimum=1
            )
            faculty_id = parse_int(
                request.form.get("faculty_id"),
                "Faculty",
                minimum=1,
                required=False
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("subjects"))

        query = """
            INSERT INTO subject
            (
                subject_code,
                subject_name,
                credits,
                semester,
                course_id,
                faculty_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            subject_code,
            subject_name,
            credits,
            semester,
            course_id,
            faculty_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error adding subject: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("subjects"))

    cursor.execute("""
        SELECT
            course_id,
            course_name
        FROM course
        ORDER BY course_name
    """)

    courses = cursor.fetchall()

    cursor.execute("""
        SELECT
            faculty_id,
            name
        FROM faculty
        ORDER BY name
    """)

    faculty = cursor.fetchall()

    cursor.execute("""
        SELECT
            s.subject_id,
            s.subject_code,
            s.subject_name,
            s.credits,
            s.semester,
            c.course_name,
            f.name AS faculty_name
        FROM subject s
        JOIN course c
            ON s.course_id = c.course_id
        LEFT JOIN faculty f
            ON s.faculty_id = f.faculty_id
        ORDER BY s.subject_code
    """)

    subjects_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subjects.html",
        subjects=subjects_data,
        courses=courses,
        faculty=faculty
    )


# =========================================================
# Edit Subject
# =========================================================

@app.route("/subjects/edit/<int:subject_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_subject(subject_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            subject_code = clean_text(
                request.form.get("subject_code"),
                "Subject code",
                20
            )
            subject_name = clean_text(
                request.form.get("subject_name"),
                "Subject name",
                100
            )
            credits = parse_int(
                request.form.get("credits"),
                "Credits",
                minimum=1,
                maximum=10
            )
            semester = parse_int(
                request.form.get("semester"),
                "Semester",
                minimum=1,
                maximum=8
            )
            course_id = parse_int(
                request.form.get("course_id"),
                "Course",
                minimum=1
            )
            faculty_id = parse_int(
                request.form.get("faculty_id"),
                "Faculty",
                minimum=1,
                required=False
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_subject", subject_id=subject_id))

        query = """
            UPDATE subject
            SET
                subject_code = %s,
                subject_name = %s,
                credits = %s,
                semester = %s,
                course_id = %s,
                faculty_id = %s
            WHERE subject_id = %s
        """

        values = (
            subject_code,
            subject_name,
            credits,
            semester,
            course_id,
            faculty_id,
            subject_id
        )

        try:

            cursor.execute(query, values)
            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating subject: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("subjects"))

    cursor.execute("""
        SELECT
            subject_id,
            subject_code,
            subject_name,
            credits,
            semester,
            course_id,
            faculty_id
        FROM subject
        WHERE subject_id = %s
    """, (subject_id,))

    subject = cursor.fetchone()

    cursor.execute("""
        SELECT
            course_id,
            course_name
        FROM course
        ORDER BY course_name
    """)

    courses = cursor.fetchall()

    cursor.execute("""
        SELECT
            faculty_id,
            name
        FROM faculty
        ORDER BY name
    """)

    faculty = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_subject.html",
        subject=subject,
        courses=courses,
        faculty=faculty
    )


# =========================================================
# Delete Subject
# =========================================================

@app.route("/subjects/delete/<int:subject_id>", methods=["POST"])
@role_required("ADMIN")
def delete_subject(subject_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM subject
            WHERE subject_id = %s
        """, (subject_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting subject: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("subjects"))


# =========================================================
# Exams
# =========================================================

@app.route("/exams", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL")
def exams():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            exam_id = parse_int(
                request.form.get("exam_id"),
                "Exam",
                minimum=1
            )
            subject_id = parse_int(
                request.form.get("subject_id"),
                "Subject",
                minimum=1
            )
            exam_date = validate_date(
                request.form.get("exam_date"),
                "Exam date"
            )
            exam_time = validate_time(
                request.form.get("exam_time"),
                "Exam time"
            )
            room_no = clean_text(
                request.form.get("room_no"),
                "Room number",
                20
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("exams"))

        try:

            cursor.execute("""
                INSERT INTO Exam_Schedule
                (
                    exam_id,
                    subject_id,
                    exam_date,
                    exam_time,
                    room_no
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                exam_id,
                subject_id,
                exam_date,
                exam_time,
                room_no
            ))

            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error adding exam schedule: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("exams"))

    cursor.execute("""
        SELECT
            es.schedule_id,
            e.exam_name,
            e.semester,
            e.academic_year,
            s.subject_code,
            s.subject_name,
            es.exam_date,
            es.exam_time,
            es.room_no
        FROM Exam_Schedule es
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject s
            ON es.subject_id = s.subject_id
        ORDER BY es.exam_date, es.exam_time
    """)

    exams_data = cursor.fetchall()
    cursor.execute("""
        SELECT
            exam_id,
            exam_name,
            semester,
            academic_year
        FROM exam
        ORDER BY exam_id
    """)

    exam_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            subject_id,
            subject_code,
            subject_name
        FROM subject
        ORDER BY subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exams.html",
        exams=exams_data,
        exam_list=exam_list,
        subjects=subjects
    )


# =========================================================
# Edit Exam
# =========================================================

@app.route("/edit_exam/<int:schedule_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_exam(schedule_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            exam_id = parse_int(
                request.form.get("exam_id"),
                "Exam",
                minimum=1
            )
            subject_id = parse_int(
                request.form.get("subject_id"),
                "Subject",
                minimum=1
            )
            exam_date = validate_date(
                request.form.get("exam_date"),
                "Exam date"
            )
            exam_time = validate_time(
                request.form.get("exam_time"),
                "Exam time"
            )
            room_no = clean_text(
                request.form.get("room_no"),
                "Room number",
                20
            )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_exam", schedule_id=schedule_id))

        try:

            cursor.execute("""
                UPDATE Exam_Schedule
                SET
                    exam_id = %s,
                    subject_id = %s,
                    exam_date = %s,
                    exam_time = %s,
                    room_no = %s
                WHERE schedule_id = %s
            """, (
                exam_id,
                subject_id,
                exam_date,
                exam_time,
                room_no,
                schedule_id
            ))

            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating exam schedule: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("exams"))

    cursor.execute("""
        SELECT *
        FROM Exam_Schedule
        WHERE schedule_id = %s
    """, (schedule_id,))

    schedule = cursor.fetchone()

    cursor.execute("""
        SELECT
            exam_id,
            exam_name,
            semester,
            academic_year
        FROM exam
        ORDER BY exam_id
    """)

    exam_list = cursor.fetchall()

    cursor.execute("""
        SELECT
            subject_id,
            subject_code,
            subject_name
        FROM subject
        ORDER BY subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "edit_exam.html",
        schedule=schedule,
        exam_list=exam_list,
        subjects=subjects
    )


# =========================================================
# Delete Exam
# =========================================================

@app.route("/delete_exam/<int:schedule_id>", methods=["POST"])
@role_required("ADMIN")
def delete_exam(schedule_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM Exam_Schedule
            WHERE schedule_id = %s
        """, (schedule_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting exam schedule: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("exams"))


# =========================================================
# Results
# =========================================================

@app.route("/results", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL", "FACULTY")
def results():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            r.result_id,
            st.student_id,
            st.roll_no,
            st.name AS student_name,
            e.exam_name,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        ORDER BY st.roll_no, e.exam_id
    """)

    results_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "results.html",
        results=results_data
    )


# =========================================================
# Edit Result
# =========================================================

@app.route("/edit_result/<int:result_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_result(result_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            total_marks = parse_float(
                request.form.get("total_marks"),
                "Total marks",
                minimum=0
            )
            percentage = parse_float(
                request.form.get("percentage"),
                "Percentage",
                minimum=0,
                maximum=100
            )
            grade = clean_text(
                request.form.get("grade"),
                "Grade",
                5
            ).upper()
            result_status = clean_text(
                request.form.get("result_status"),
                "Result status",
                10
            ).upper()

            if grade not in {"A+", "A", "B+", "B", "C", "D", "F"}:
                raise ValueError("Please enter a valid grade.")

            if result_status not in {"PASS", "FAIL"}:
                raise ValueError("Result status must be PASS or FAIL.")

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_result", result_id=result_id))

        try:

            cursor.execute("""
                UPDATE result
                SET
                    total_marks = %s,
                    percentage = %s,
                    grade = %s,
                    result_status = %s
                WHERE result_id = %s
            """, (
                total_marks,
                percentage,
                grade,
                result_status,
                result_id
            ))

            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating result: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("results"))

    cursor.execute("""
        SELECT
            r.result_id,
            st.roll_no,
            st.name AS student_name,
            e.exam_name,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        WHERE r.result_id = %s
    """, (result_id,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_result.html",
        result=result
    )


# =========================================================
# Delete Result
# =========================================================

@app.route("/delete_result/<int:result_id>", methods=["POST"])
@role_required("ADMIN")
def delete_result(result_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM result
            WHERE result_id = %s
        """, (result_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting result: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("results"))


# =========================================================
# Attendance
# =========================================================

@app.route("/attendance", methods=["GET", "POST"])
@role_required("ADMIN", "PRINCIPAL", "FACULTY")
def attendance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            a.attendance_id,
            st.student_id,
            st.roll_no,
            st.name AS student_name,
            sub.subject_code,
            sub.subject_name,
            a.total_classes,
            a.attended_classes,
            ROUND(
                (a.attended_classes / a.total_classes) * 100,
                2
            ) AS attendance_percentage
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN subject sub
            ON a.subject_id = sub.subject_id
        ORDER BY st.roll_no, sub.subject_code
    """)

    attendance_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance.html",
        attendance=attendance_data
    )


# =========================================================
# Edit Attendance
# =========================================================

@app.route("/edit_attendance/<int:attendance_id>", methods=["GET", "POST"])
@role_required("ADMIN")
def edit_attendance(attendance_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == "POST":

        try:
            total_classes = parse_int(
                request.form.get("total_classes"),
                "Total classes",
                minimum=1
            )
            attended_classes = parse_int(
                request.form.get("attended_classes"),
                "Attended classes",
                minimum=0
            )

            if attended_classes > total_classes:
                raise ValueError(
                    "Attended classes cannot be greater than total classes."
                )

        except ValueError as e:
            flash(str(e), "error")
            cursor.close()
            connection.close()
            return redirect(url_for("edit_attendance", attendance_id=attendance_id))

        try:

            cursor.execute("""
                UPDATE attendance
                SET
                    total_classes = %s,
                    attended_classes = %s
                WHERE attendance_id = %s
            """, (
                total_classes,
                attended_classes,
                attendance_id
            ))

            connection.commit()

        except Exception as e:

            connection.rollback()
            cursor.close()
            connection.close()

            return f"Error updating attendance: {e}"

        cursor.close()
        connection.close()

        return redirect(url_for("attendance"))

    cursor.execute("""
        SELECT
            a.attendance_id,
            st.roll_no,
            st.name AS student_name,
            sub.subject_code,
            sub.subject_name,
            a.total_classes,
            a.attended_classes
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN subject sub
            ON a.subject_id = sub.subject_id
        WHERE a.attendance_id = %s
    """, (attendance_id,))

    record = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "edit_attendance.html",
        attendance=record
    )


# =========================================================
# Delete Attendance
# =========================================================

@app.route("/delete_attendance/<int:attendance_id>", methods=["POST"])
@role_required("ADMIN")
def delete_attendance(attendance_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM attendance
            WHERE attendance_id = %s
        """, (attendance_id,))

        connection.commit()

    except Exception as e:

        connection.rollback()
        cursor.close()
        connection.close()

        return f"Error deleting attendance: {e}"

    cursor.close()
    connection.close()

    return redirect(url_for("attendance"))


# =========================================================
# Student Performance
# =========================================================

@app.route("/student-performance/<int:student_id>")
@login_required
def student_performance(student_id):

    role = session.get("role")

    if role not in ("ADMIN", "PRINCIPAL", "FACULTY"):
        if role != "STUDENT" or session.get("student_id") != student_id:
            abort(403)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    performance = []

    try:
        cursor.callproc(
            "GetStudentPerformance",
            (student_id,)
        )

        for result in cursor.stored_results():
            performance = result.fetchall()

    finally:
        cursor.close()
        connection.close()

    return render_template(
        "student_performance.html",
        performance=performance
    )

# =========================================================
# Student Attendance
# =========================================================

@app.route("/student-attendance/<int:student_id>")
@login_required
def student_attendance(student_id):

    role = session.get("role")

    if role not in ("ADMIN", "PRINCIPAL", "FACULTY"):
       if role != "STUDENT" or session.get("student_id") != student_id:
         abort(403)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.callproc(
        "GetStudentAttendance",
        (student_id,)
    )

    attendance_data = []

    for result in cursor.stored_results():
        attendance_data = result.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_attendance.html",
        attendance=attendance_data
    )


# =========================================================
# Student Dashboard
# =========================================================

@app.route("/student-dashboard/<int:student_id>")
@login_required
def student_dashboard(student_id):

    role = session.get("role")
    if role not in ("ADMIN", "PRINCIPAL"):
        if role != "STUDENT" or session.get("student_id") != student_id:
            abort(403)

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            s.student_id,
            s.roll_no,
            s.name,
            s.email,
            s.phone,
            s.admission_year,
            c.course_name
        FROM student s
        JOIN course c
            ON s.course_id = c.course_id
        WHERE s.student_id = %s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:

        cursor.close()
        connection.close()

        return render_template(
            "student_dashboard.html",
            student=None
        )

    cursor.execute("""
        SELECT
            COALESCE(
                ROUND(
                    SUM(attended_classes) /
                    NULLIF(SUM(total_classes), 0) * 100,
                    2
                ),
                0
            ) AS attendance_percentage
        FROM attendance
        WHERE student_id = %s
    """, (student_id,))

    attendance_data = cursor.fetchone()

    attendance_percentage = attendance_data["attendance_percentage"]

    cursor.execute("""
        SELECT COUNT(*) AS result_count
        FROM result
        WHERE student_id = %s
    """, (student_id,))

    result_data = cursor.fetchone()

    result_count = result_data["result_count"]

    cursor.execute("""
        SELECT percentage
        FROM result
        WHERE student_id = %s
        ORDER BY exam_id DESC
        LIMIT 1
    """, (student_id,))

    latest_result = cursor.fetchone()

    if latest_result:
        latest_percentage = latest_result["percentage"]
    else:
        latest_percentage = 0

    cursor.close()
    connection.close()

    return render_template(
        "student_dashboard.html",
        student=student,
        attendance_percentage=attendance_percentage,
        result_count=result_count,
        latest_percentage=latest_percentage
    )


# =========================================================
# Attendance Summary
# =========================================================

@app.route("/attendance-summary")
@role_required("ADMIN", "PRINCIPAL")
def attendance_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.student_id,
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            SUM(a.total_classes) AS total_classes,
            SUM(a.attended_classes) AS attended_classes,
            ROUND(
                (
                    SUM(a.attended_classes) /
                    NULLIF(SUM(a.total_classes), 0)
                ) * 100,
                2
            ) AS attendance_percentage
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name
        ORDER BY attendance_percentage DESC
    """)

    summary = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance_summary.html",
        summary=summary
    )


# =========================================================
# Course Performance
# =========================================================

@app.route("/course-performance")
@role_required("ADMIN", "PRINCIPAL")
def course_performance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_name,
            COUNT(DISTINCT r.student_id) AS total_students,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        GROUP BY
            c.course_id,
            c.course_name
        ORDER BY average_percentage DESC
    """)

    performance = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_performance.html",
        performance=performance
    )


# =========================================================
# Course Student Report
# =========================================================

@app.route("/course-student-report")
@role_required("ADMIN", "PRINCIPAL")
def course_student_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            d.dept_name,
            COUNT(s.student_id) AS student_count
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        LEFT JOIN student s
            ON c.course_id = s.course_id
        GROUP BY
            c.course_id,
            c.course_name,
            d.dept_name
        ORDER BY c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_student_report.html",
        courses=courses
    )


# =========================================================
# Department Student Report
# =========================================================

@app.route("/department-student-report")
@role_required("ADMIN", "PRINCIPAL")
def department_student_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(s.student_id) AS student_count
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN student s
            ON c.course_id = s.course_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_student_report.html",
        departments=departments
    )


# =========================================================
# Department Faculty Report
# =========================================================

@app.route("/department-faculty-report")
@role_required("ADMIN", "PRINCIPAL")
def department_faculty_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(f.faculty_id) AS faculty_count
        FROM department d
        LEFT JOIN faculty f
            ON d.dept_id = f.dept_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_faculty_report.html",
        departments=departments
    )


# =========================================================
# Subject Faculty Report
# =========================================================

@app.route("/subject-faculty-report")
@role_required("ADMIN", "PRINCIPAL")
def subject_faculty_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            sub.credits,
            sub.semester,
            c.course_name,
            COALESCE(f.name, 'Not Assigned') AS faculty_name
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN faculty f
            ON sub.faculty_id = f.faculty_id
        ORDER BY sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subject_faculty_report.html",
        subjects=subjects
    )


# =========================================================
# Exam Schedule Report
# =========================================================

@app.route("/exam-schedule-report")
@role_required("ADMIN", "PRINCIPAL")
def exam_schedule_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            es.schedule_id,
            e.exam_name,
            e.academic_year,
            e.semester,
            sub.subject_code,
            sub.subject_name,
            es.exam_date,
            es.exam_time,
            es.room_no
        FROM Exam_Schedule es
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        ORDER BY es.exam_date, es.exam_time
    """)

    schedules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_schedule_report.html",
        schedules=schedules
    )


# =========================================================
# Student Marks Report
# =========================================================

@app.route("/student-marks-report")
@role_required("ADMIN", "PRINCIPAL")
def student_marks_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            e.exam_name,
            sub.subject_code,
            sub.subject_name,
            m.marks_obtained,
            m.max_marks,
            ROUND(
                (m.marks_obtained / m.max_marks) * 100,
                2
            ) AS percentage
        FROM marks m
        JOIN student st
            ON m.student_id = st.student_id
        JOIN Exam_Schedule es
            ON m.schedule_id = es.schedule_id
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        ORDER BY
            st.roll_no,
            e.exam_id,
            sub.subject_code
    """)

    marks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_marks_report.html",
        marks=marks
    )


# =========================================================
# Result Summary Report
# =========================================================

@app.route("/result-summary-report")
@role_required("ADMIN", "PRINCIPAL")
def result_summary_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        ORDER BY
            e.exam_id,
            r.percentage DESC
    """)

    results_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "result_summary_report.html",
        results=results_data
    )


# =========================================================
# Course Performance Report
# =========================================================

@app.route("/course-performance-report")
@role_required("ADMIN", "PRINCIPAL")
def course_performance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            COUNT(r.result_id) AS students_with_results,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage
        FROM course c
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            c.course_id,
            c.course_name
        ORDER BY average_percentage DESC
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_performance_report.html",
        courses=courses
    )


# =========================================================
# Student Attendance Report
# =========================================================

@app.route("/student-attendance-report")
@role_required("ADMIN", "PRINCIPAL")
def student_attendance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            sub.subject_code,
            sub.subject_name,
            a.total_classes,
            a.attended_classes,
            ROUND(
                (a.attended_classes / a.total_classes) * 100,
                2
            ) AS attendance_percentage
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN subject sub
            ON a.subject_id = sub.subject_id
        ORDER BY
            st.roll_no,
            sub.subject_code
    """)

    attendance_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_attendance_report.html",
        attendance=attendance_data
    )


# =========================================================
# Department Performance Report
# =========================================================

@app.route("/department-performance-report")
@role_required("ADMIN", "PRINCIPAL")
def department_performance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(DISTINCT r.student_id) AS students_with_results,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_performance_report.html",
        departments=departments
    )


# =========================================================
# Subject Performance Report
# =========================================================

@app.route("/subject-performance-report")
@role_required("ADMIN", "PRINCIPAL")
def subject_performance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            COUNT(m.mark_id) AS students_with_marks,
            ROUND(
                AVG((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS average_percentage,
            ROUND(
                MAX((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS highest_percentage,
            ROUND(
                MIN((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS lowest_percentage
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN Exam_Schedule es
            ON sub.subject_id = es.subject_id
        LEFT JOIN marks m
            ON es.schedule_id = m.schedule_id
        GROUP BY
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name
        ORDER BY sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subject_performance_report.html",
        subjects=subjects
    )


# =========================================================
# Faculty Workload Report
# =========================================================

@app.route("/faculty-workload-report")
@role_required("ADMIN", "PRINCIPAL")
def faculty_workload_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            d.dept_name,
            COUNT(sub.subject_id) AS subject_count
        FROM faculty f
        JOIN department d
            ON f.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON f.faculty_id = sub.faculty_id
        GROUP BY
            f.faculty_id,
            f.name,
            d.dept_name
        ORDER BY
            d.dept_name,
            f.name
    """)

    faculty = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "faculty_workload_report.html",
        faculty=faculty
    )


# =========================================================
# Course Subject Report
# =========================================================

@app.route("/course-subject-report")
@role_required("ADMIN", "PRINCIPAL")
def course_subject_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_name,
            d.dept_name,
            sub.subject_code,
            sub.subject_name,
            sub.credits,
            sub.semester,
            COALESCE(f.name, 'Not Assigned') AS faculty_name
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON c.course_id = sub.course_id
        LEFT JOIN faculty f
            ON sub.faculty_id = f.faculty_id
        ORDER BY
            c.course_name,
            sub.semester,
            sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_subject_report.html",
        subjects=subjects
    )


# =========================================================
# Student Result Analysis
# =========================================================

@app.route("/student-result-analysis")
@role_required("ADMIN", "PRINCIPAL")
def student_result_analysis():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            r.percentage,
            r.grade,
            CASE
                WHEN r.percentage >= 90 THEN 'Excellent'
                WHEN r.percentage >= 75 THEN 'Very Good'
                WHEN r.percentage >= 60 THEN 'Good'
                WHEN r.percentage >= 50 THEN 'Average'
                ELSE 'Needs Improvement'
            END AS performance_category
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        ORDER BY
            r.percentage DESC
    """)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_result_analysis.html",
        results=results
    )


# =========================================================
# Student Rank Report
# =========================================================

@app.route("/student-rank-report")
@role_required("ADMIN", "PRINCIPAL")
def student_rank_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            roll_no,
            student_name,
            course_name,
            exam_name,
            percentage,
            grade,
            RANK() OVER (
                PARTITION BY exam_name
                ORDER BY percentage DESC
            ) AS student_rank
        FROM (
            SELECT
                st.roll_no,
                st.name AS student_name,
                c.course_name,
                e.exam_name,
                r.percentage,
                r.grade
            FROM result r
            JOIN student st
                ON r.student_id = st.student_id
            JOIN course c
                ON st.course_id = c.course_id
            JOIN exam e
                ON r.exam_id = e.exam_id
        ) AS result_data
        ORDER BY
            exam_name,
            student_rank
    """)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_rank_report.html",
        results=results
    )


# =========================================================
# Exam Result Summary
# =========================================================

@app.route("/exam-result-summary")
@role_required("ADMIN", "PRINCIPAL")
def exam_result_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester,
            COUNT(r.result_id) AS total_students,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage,
            SUM(
                CASE
                    WHEN r.result_status = 'PASS' THEN 1
                    ELSE 0
                END
            ) AS passed_students,
            SUM(
                CASE
                    WHEN r.result_status = 'FAIL' THEN 1
                    ELSE 0
                END
            ) AS failed_students
        FROM exam e
        LEFT JOIN result r
            ON e.exam_id = r.exam_id
        GROUP BY
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester
        ORDER BY e.exam_id
    """)

    exams = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_result_summary.html",
        exams=exams
    )


# =========================================================
# Attendance Defaulters
# =========================================================

@app.route("/attendance-defaulters")
@role_required("ADMIN", "PRINCIPAL")
def attendance_defaulters():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            SUM(a.total_classes) AS total_classes,
            SUM(a.attended_classes) AS attended_classes,
            ROUND(
                SUM(a.attended_classes) /
                NULLIF(SUM(a.total_classes), 0) * 100,
                2
            ) AS attendance_percentage
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name
        HAVING
            attendance_percentage < 75
        ORDER BY
            attendance_percentage
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "attendance_defaulters.html",
        students=students
    )


# =========================================================
# Course Attendance Summary
# =========================================================

@app.route("/course-attendance-summary")
@role_required("ADMIN", "PRINCIPAL")
def course_attendance_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            COUNT(DISTINCT a.student_id) AS students_with_attendance,
            SUM(a.total_classes) AS total_classes,
            SUM(a.attended_classes) AS attended_classes,
            ROUND(
                SUM(a.attended_classes) /
                NULLIF(SUM(a.total_classes), 0) * 100,
                2
            ) AS attendance_percentage
        FROM course c
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN attendance a
            ON st.student_id = a.student_id
        GROUP BY
            c.course_id,
            c.course_name
        ORDER BY
            c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_attendance_summary.html",
        courses=courses
    )


# =========================================================
# Subject Attendance Report
# =========================================================

@app.route("/subject-attendance-report")
@role_required("ADMIN", "PRINCIPAL")
def subject_attendance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            COUNT(DISTINCT a.student_id) AS students_count,
            COALESCE(SUM(a.total_classes), 0) AS total_classes,
            COALESCE(SUM(a.attended_classes), 0) AS attended_classes,
            ROUND(
                COALESCE(SUM(a.attended_classes), 0) /
                NULLIF(COALESCE(SUM(a.total_classes), 0), 0) * 100,
                2
            ) AS attendance_percentage
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN attendance a
            ON sub.subject_id = a.subject_id
        GROUP BY
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name
        ORDER BY
            sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subject_attendance_report.html",
        subjects=subjects
    )


# =========================================================
# Student Attendance Detail
# =========================================================

@app.route("/student-attendance-detail")
@role_required("ADMIN", "PRINCIPAL")
def student_attendance_detail():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            sub.subject_code,
            sub.subject_name,
            a.total_classes,
            a.attended_classes,
            (a.total_classes - a.attended_classes) AS absent_classes,
            ROUND(
                (a.attended_classes / a.total_classes) * 100,
                2
            ) AS attendance_percentage
        FROM attendance a
        JOIN student st
            ON a.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN subject sub
            ON a.subject_id = sub.subject_id
        ORDER BY
            st.roll_no,
            sub.subject_code
    """)

    attendance = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_attendance_detail.html",
        attendance=attendance
    )


# =========================================================
# Student Marks Detail
# =========================================================

@app.route("/student-marks-detail")
@role_required("ADMIN", "PRINCIPAL")
def student_marks_detail():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            sub.subject_code,
            sub.subject_name,
            m.marks_obtained,
            m.max_marks,
            ROUND(
                (m.marks_obtained / m.max_marks) * 100,
                2
            ) AS percentage,
            CASE
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 90
                    THEN 'A+'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 80
                    THEN 'A'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 70
                    THEN 'B'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 60
                    THEN 'C'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 50
                    THEN 'D'
                ELSE 'F'
            END AS grade
        FROM marks m
        JOIN student st
            ON m.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN Exam_Schedule es
            ON m.schedule_id = es.schedule_id
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        ORDER BY
            st.roll_no,
            e.exam_id,
            sub.subject_code
    """)

    marks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_marks_detail.html",
        marks=marks
    )


# =========================================================
# Top Students Report
# =========================================================

@app.route("/top-students-report")
@role_required("ADMIN", "PRINCIPAL")
def top_students_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            COUNT(r.result_id) AS exams_count,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage
        FROM student st
        JOIN course c
            ON st.course_id = c.course_id
        JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name
        ORDER BY
            average_percentage DESC
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "top_students_report.html",
        students=students
    )


# =========================================================
# Failed Students Report
# =========================================================

@app.route("/failed-students-report")
@role_required("ADMIN", "PRINCIPAL")
def failed_students_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        WHERE r.result_status = 'FAIL'
        ORDER BY
            r.percentage
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "failed_students_report.html",
        students=students
    )


# =========================================================
# Passed Students Report
# =========================================================

@app.route("/passed-students-report")
@role_required("ADMIN", "PRINCIPAL")
def passed_students_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        WHERE r.result_status = 'PASS'
        ORDER BY
            r.percentage DESC
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "passed_students_report.html",
        students=students
    )


# =========================================================
# Department Result Summary
# =========================================================

@app.route("/department-result-summary")
@role_required("ADMIN", "PRINCIPAL")
def department_result_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(r.result_id) AS total_results,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage,
            SUM(
                CASE
                    WHEN r.result_status = 'PASS' THEN 1
                    ELSE 0
                END
            ) AS passed_students,
            SUM(
                CASE
                    WHEN r.result_status = 'FAIL' THEN 1
                    ELSE 0
                END
            ) AS failed_students
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_result_summary.html",
        departments=departments
    )


# =========================================================
# Course Result Comparison
# =========================================================

@app.route("/course-result-comparison")
@role_required("ADMIN", "PRINCIPAL")
def course_result_comparison():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            COUNT(DISTINCT r.student_id) AS students_with_results,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage
        FROM course c
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            c.course_id,
            c.course_name
        ORDER BY
            average_percentage DESC
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_result_comparison.html",
        courses=courses
    )


# =========================================================
# Course Pass Fail Summary
# =========================================================

@app.route("/course-pass-fail-summary")
@role_required("ADMIN", "PRINCIPAL")
def course_pass_fail_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            COUNT(r.result_id) AS total_results,
            SUM(
                CASE
                    WHEN r.result_status = 'PASS' THEN 1
                    ELSE 0
                END
            ) AS passed_students,
            SUM(
                CASE
                    WHEN r.result_status = 'FAIL' THEN 1
                    ELSE 0
                END
            ) AS failed_students,
            ROUND(
                SUM(
                    CASE
                        WHEN r.result_status = 'PASS' THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(r.result_id), 0) * 100,
                2
            ) AS pass_percentage
        FROM course c
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            c.course_id,
            c.course_name
        ORDER BY
            c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_pass_fail_summary.html",
        courses=courses
    )


# =========================================================
# Student Pass Fail Summary
# =========================================================

@app.route("/student-pass-fail-summary")
@role_required("ADMIN", "PRINCIPAL")
def student_pass_fail_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            COUNT(r.result_id) AS total_results,
            SUM(
                CASE
                    WHEN r.result_status = 'PASS' THEN 1
                    ELSE 0
                END
            ) AS passed_exams,
            SUM(
                CASE
                    WHEN r.result_status = 'FAIL' THEN 1
                    ELSE 0
                END
            ) AS failed_exams,
            ROUND(
                SUM(
                    CASE
                        WHEN r.result_status = 'PASS' THEN 1
                        ELSE 0
                    END
                ) / NULLIF(COUNT(r.result_id), 0) * 100,
                2
            ) AS pass_percentage
        FROM student st
        JOIN course c
            ON st.course_id = c.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name
        ORDER BY
            st.roll_no
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_pass_fail_summary.html",
        students=students
    )


# =========================================================
# Student Result History
# =========================================================

@app.route("/student-result-history")
@role_required("ADMIN", "PRINCIPAL")
def student_result_history():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            e.academic_year,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        ORDER BY
            st.roll_no,
            e.exam_id
    """)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_result_history.html",
        results=results
    )


# =========================================================
# Exam Student Performance
# =========================================================

@app.route("/exam-student-performance")
@role_required("ADMIN", "PRINCIPAL")
def exam_student_performance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester,
            COUNT(r.result_id) AS total_students,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage,
            SUM(
                CASE
                    WHEN r.result_status = 'PASS' THEN 1
                    ELSE 0
                END
            ) AS passed_students,
            SUM(
                CASE
                    WHEN r.result_status = 'FAIL' THEN 1
                    ELSE 0
                END
            ) AS failed_students
        FROM exam e
        LEFT JOIN result r
            ON e.exam_id = r.exam_id
        GROUP BY
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester
        ORDER BY
            e.exam_id
    """)

    exams = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_student_performance.html",
        exams=exams
    )


# =========================================================
# Faculty Subject Allocation
# =========================================================

@app.route("/faculty-subject-allocation")
@role_required("ADMIN", "PRINCIPAL")
def faculty_subject_allocation():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            d.dept_name,
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            sub.credits,
            sub.semester
        FROM faculty f
        JOIN department d
            ON f.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON f.faculty_id = sub.faculty_id
        LEFT JOIN course c
            ON sub.course_id = c.course_id
        ORDER BY
            f.name,
            sub.semester,
            sub.subject_code
    """)

    faculty = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "faculty_subject_allocation.html",
        faculty=faculty
    )


# =========================================================
# Department Subject Summary
# =========================================================

@app.route("/department-subject-summary")
@role_required("ADMIN", "PRINCIPAL")
def department_subject_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(DISTINCT sub.subject_id) AS total_subjects,
            COUNT(DISTINCT c.course_id) AS total_courses,
            COALESCE(SUM(sub.credits), 0) AS total_credits
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN subject sub
            ON c.course_id = sub.course_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_subject_summary.html",
        departments=departments
    )


# =========================================================
# Course Student Count
# =========================================================

@app.route("/course-student-count")
@role_required("ADMIN", "PRINCIPAL")
def course_student_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            d.dept_name,
            COUNT(s.student_id) AS student_count
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        LEFT JOIN student s
            ON c.course_id = s.course_id
        GROUP BY
            c.course_id,
            c.course_name,
            d.dept_name
        ORDER BY
            c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_student_count.html",
        courses=courses
    )


# =========================================================
# Semester Subject Report
# =========================================================

@app.route("/semester-subject-report")
@role_required("ADMIN", "PRINCIPAL")
def semester_subject_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.semester,
            c.course_name,
            sub.subject_code,
            sub.subject_name,
            sub.credits,
            COALESCE(f.name, 'Not Assigned') AS faculty_name
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN faculty f
            ON sub.faculty_id = f.faculty_id
        ORDER BY
            sub.semester,
            c.course_name,
            sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "semester_subject_report.html",
        subjects=subjects
    )


# =========================================================
# Student Attendance Summary
# =========================================================

@app.route("/student-attendance-summary")
@role_required("ADMIN", "PRINCIPAL")
def student_attendance_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            COALESCE(SUM(a.total_classes), 0) AS total_classes,
            COALESCE(SUM(a.attended_classes), 0) AS attended_classes,
            COALESCE(
                SUM(a.total_classes) - SUM(a.attended_classes),
                0
            ) AS absent_classes,
            ROUND(
                COALESCE(
                    SUM(a.attended_classes) /
                    NULLIF(SUM(a.total_classes), 0) * 100,
                    0
                ),
                2
            ) AS attendance_percentage
        FROM student st
        JOIN course c
            ON st.course_id = c.course_id
        LEFT JOIN attendance a
            ON st.student_id = a.student_id
        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name
        ORDER BY
            st.roll_no
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_attendance_summary.html",
        students=students
    )


# =========================================================
# Faculty Subject Count
# =========================================================

@app.route("/faculty-subject-count")
@role_required("ADMIN", "PRINCIPAL")
def faculty_subject_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            d.dept_name,
            COUNT(sub.subject_id) AS subject_count
        FROM faculty f
        JOIN department d
            ON f.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON f.faculty_id = sub.faculty_id
        GROUP BY
            f.faculty_id,
            f.name,
            d.dept_name
        ORDER BY
            f.name
    """)

    faculty = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "faculty_subject_count.html",
        faculty=faculty
    )


# =========================================================
# Department Faculty Count
# =========================================================

@app.route("/department-faculty-count")
@role_required("ADMIN", "PRINCIPAL")
def department_faculty_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(f.faculty_id) AS faculty_count
        FROM department d
        LEFT JOIN faculty f
            ON d.dept_id = f.dept_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_faculty_count.html",
        departments=departments
    )


# =========================================================
# Exam Schedule Course Report
# =========================================================

@app.route("/exam-schedule-course-report")
@role_required("ADMIN", "PRINCIPAL")
def exam_schedule_course_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_name,
            e.academic_year,
            e.semester,
            c.course_name,
            sub.subject_code,
            sub.subject_name,
            es.exam_date,
            es.exam_time,
            es.room_no
        FROM Exam_Schedule es
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        JOIN course c
            ON sub.course_id = c.course_id
        ORDER BY
            e.exam_id,
            c.course_name,
            es.exam_date
    """)

    schedules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_schedule_course_report.html",
        schedules=schedules
    )


# =========================================================
# Student Exam Schedule
# =========================================================

@app.route("/student-exam-schedule")
@role_required("ADMIN", "PRINCIPAL")
def student_exam_schedule():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            sub.subject_code,
            sub.subject_name,
            es.exam_date,
            es.exam_time,
            es.room_no
        FROM student st
        JOIN course c
            ON st.course_id = c.course_id
        JOIN subject sub
            ON c.course_id = sub.course_id
        JOIN Exam_Schedule es
            ON sub.subject_id = es.subject_id
        JOIN exam e
            ON es.exam_id = e.exam_id
        ORDER BY
            st.roll_no,
            es.exam_date
    """)

    schedules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_exam_schedule.html",
        schedules=schedules
    )


# =========================================================
# Student Subject Performance
# =========================================================

@app.route("/student-subject-performance")
@role_required("ADMIN", "PRINCIPAL")
def student_subject_performance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            sub.subject_code,
            sub.subject_name,
            m.marks_obtained,
            m.max_marks,
            ROUND(
                (m.marks_obtained / m.max_marks) * 100,
                2
            ) AS percentage,
            CASE
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 90
                    THEN 'A+'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 80
                    THEN 'A'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 70
                    THEN 'B'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 60
                    THEN 'C'
                WHEN (m.marks_obtained / m.max_marks) * 100 >= 50
                    THEN 'D'
                ELSE 'F'
            END AS grade
        FROM marks m
        JOIN student st
            ON m.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN Exam_Schedule es
            ON m.schedule_id = es.schedule_id
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        ORDER BY
            st.roll_no,
            e.exam_id,
            sub.subject_code
    """)

    performance = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_subject_performance.html",
        performance=performance
    )


# =========================================================
# Subject Marks Summary
# =========================================================

@app.route("/subject-marks-summary")
@role_required("ADMIN", "PRINCIPAL")
def subject_marks_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            COUNT(m.mark_id) AS students_count,
            ROUND(
                AVG((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS average_percentage,
            ROUND(
                MAX((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS highest_percentage,
            ROUND(
                MIN((m.marks_obtained / m.max_marks) * 100),
                2
            ) AS lowest_percentage
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN Exam_Schedule es
            ON sub.subject_id = es.subject_id
        LEFT JOIN marks m
            ON es.schedule_id = m.schedule_id
        GROUP BY
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name
        ORDER BY
            sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subject_marks_summary.html",
        subjects=subjects
    )


# =========================================================
# Department Attendance Summary
# =========================================================

@app.route("/department-attendance-summary")
@role_required("ADMIN", "PRINCIPAL")
def department_attendance_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(DISTINCT a.student_id) AS students_count,
            COALESCE(SUM(a.total_classes), 0) AS total_classes,
            COALESCE(SUM(a.attended_classes), 0) AS attended_classes,
            COALESCE(
                SUM(a.total_classes) - SUM(a.attended_classes),
                0
            ) AS absent_classes,
            ROUND(
                COALESCE(
                    SUM(a.attended_classes) /
                    NULLIF(SUM(a.total_classes), 0) * 100,
                    0
                ),
                2
            ) AS attendance_percentage
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN attendance a
            ON st.student_id = a.student_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_attendance_summary.html",
        departments=departments
    )


# =========================================================
# Department Academic Overview
# =========================================================

@app.route("/department-academic-overview")
@role_required("ADMIN", "PRINCIPAL")
def department_academic_overview():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(DISTINCT st.student_id) AS students_count,

            ROUND(
                COALESCE(AVG(r.percentage), 0),
                2
            ) AS average_percentage,

            ROUND(
                COALESCE(
                    SUM(a.attended_classes) /
                    NULLIF(SUM(a.total_classes), 0) * 100,
                    0
                ),
                2
            ) AS attendance_percentage

        FROM department d

        LEFT JOIN course c
            ON d.dept_id = c.dept_id

        LEFT JOIN student st
            ON c.course_id = st.course_id

        LEFT JOIN result r
            ON st.student_id = r.student_id

        LEFT JOIN attendance a
            ON st.student_id = a.student_id

        GROUP BY
            d.dept_id,
            d.dept_name

        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_academic_overview.html",
        departments=departments
    )


# =========================================================
# Department Student Performance
# =========================================================

@app.route("/department-student-performance")
@role_required("ADMIN", "PRINCIPAL")
def department_student_performance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            d.dept_id,
            d.dept_name,
            COUNT(DISTINCT r.student_id) AS students_count,
            ROUND(AVG(r.percentage), 2) AS average_percentage,
            MAX(r.percentage) AS highest_percentage,
            MIN(r.percentage) AS lowest_percentage
        FROM department d
        LEFT JOIN course c
            ON d.dept_id = c.dept_id
        LEFT JOIN student st
            ON c.course_id = st.course_id
        LEFT JOIN result r
            ON st.student_id = r.student_id
        GROUP BY
            d.dept_id,
            d.dept_name
        ORDER BY
            d.dept_name
    """)

    departments = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "department_student_performance.html",
        departments=departments
    )


# =========================================================
# Student Academic Overview
# =========================================================

@app.route("/student-academic-overview")
@role_required("ADMIN", "PRINCIPAL")
def student_academic_overview():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,

            ROUND(
                COALESCE(AVG(r.percentage), 0),
                2
            ) AS average_percentage,

            ROUND(
                COALESCE(
                    SUM(a.attended_classes) /
                    NULLIF(SUM(a.total_classes), 0) * 100,
                    0
                ),
                2
            ) AS attendance_percentage

        FROM student st

        JOIN course c
            ON st.course_id = c.course_id

        LEFT JOIN result r
            ON st.student_id = r.student_id

        LEFT JOIN attendance a
            ON st.student_id = a.student_id

        GROUP BY
            st.student_id,
            st.roll_no,
            st.name,
            c.course_name

        ORDER BY
            st.roll_no
    """)

    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_academic_overview.html",
        students=students
    )


# =========================================================
# Student Result Trend
# =========================================================

@app.route("/student-result-trend")
@role_required("ADMIN", "PRINCIPAL")
def student_result_trend():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            st.roll_no,
            st.name AS student_name,
            c.course_name,
            e.exam_name,
            e.academic_year,
            r.total_marks,
            r.percentage,
            r.grade,
            r.result_status
        FROM result r
        JOIN student st
            ON r.student_id = st.student_id
        JOIN course c
            ON st.course_id = c.course_id
        JOIN exam e
            ON r.exam_id = e.exam_id
        ORDER BY
            st.roll_no,
            e.exam_id
    """)

    results = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "student_result_trend.html",
        results=results
    )


# =========================================================
# Subject Student Count
# =========================================================

@app.route("/subject-student-count")
@role_required("ADMIN", "PRINCIPAL")
def subject_student_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            COALESCE(f.name, 'Not Assigned') AS faculty_name,
            COUNT(DISTINCT st.student_id) AS student_count
        FROM subject sub
        JOIN course c
            ON sub.course_id = c.course_id
        LEFT JOIN faculty f
            ON sub.faculty_id = f.faculty_id
        LEFT JOIN student st
            ON c.course_id = st.course_id
        GROUP BY
            sub.subject_id,
            sub.subject_code,
            sub.subject_name,
            c.course_name,
            f.name
        ORDER BY
            sub.subject_code
    """)

    subjects = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "subject_student_count.html",
        subjects=subjects
    )


# =========================================================
# Exam Subject Summary
# =========================================================

@app.route("/exam-subject-summary")
@role_required("ADMIN", "PRINCIPAL")
def exam_subject_summary():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_name,
            e.academic_year,
            e.semester,
            c.course_name,
            sub.subject_code,
            sub.subject_name,
            es.exam_date,
            es.exam_time,
            es.room_no
        FROM Exam_Schedule es
        JOIN exam e
            ON es.exam_id = e.exam_id
        JOIN subject sub
            ON es.subject_id = sub.subject_id
        JOIN course c
            ON sub.course_id = c.course_id
        ORDER BY
            e.exam_id,
            es.exam_date,
            es.exam_time
    """)

    schedules = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_subject_summary.html",
        schedules=schedules
    )


# =========================================================
# Faculty Course Allocation
# =========================================================

@app.route("/faculty-course-allocation")
@role_required("ADMIN", "PRINCIPAL")
def faculty_course_allocation():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            f.faculty_id,
            f.name AS faculty_name,
            d.dept_name,
            c.course_name,
            sub.subject_code,
            sub.subject_name
        FROM faculty f
        JOIN department d
            ON f.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON f.faculty_id = sub.faculty_id
        LEFT JOIN course c
            ON sub.course_id = c.course_id
        ORDER BY
            f.name,
            c.course_name,
            sub.subject_code
    """)

    faculty = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "faculty_course_allocation.html",
        faculty=faculty
    )


# =========================================================
# Course Faculty Count
# =========================================================

@app.route("/course-faculty-count")
@role_required("ADMIN", "PRINCIPAL")
def course_faculty_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            d.dept_name,
            COUNT(DISTINCT sub.faculty_id) AS faculty_count
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON c.course_id = sub.course_id
        GROUP BY
            c.course_id,
            c.course_name,
            d.dept_name
        ORDER BY
            c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_faculty_count.html",
        courses=courses
    )


# =========================================================
# Course Subject Count
# =========================================================

@app.route("/course-subject-count")
@role_required("ADMIN", "PRINCIPAL")
def course_subject_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            c.course_id,
            c.course_name,
            d.dept_name,
            COUNT(sub.subject_id) AS subject_count
        FROM course c
        JOIN department d
            ON c.dept_id = d.dept_id
        LEFT JOIN subject sub
            ON c.course_id = sub.course_id
        GROUP BY
            c.course_id,
            c.course_name,
            d.dept_name
        ORDER BY
            c.course_name
    """)

    courses = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "course_subject_count.html",
        courses=courses
    )


# =========================================================
# Exam Student Count
# =========================================================

@app.route("/exam-student-count")
@role_required("ADMIN", "PRINCIPAL")
def exam_student_count():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester,
            COUNT(DISTINCT r.student_id) AS student_count
        FROM exam e
        LEFT JOIN result r
            ON e.exam_id = r.exam_id
        GROUP BY
            e.exam_id,
            e.exam_name,
            e.academic_year,
            e.semester
        ORDER BY
            e.exam_id
    """)

    exams = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "exam_student_count.html",
        exams=exams
    )


# =========================================================
# Session-Based Authentication
# =========================================================

registered_users = {}


# =========================================================
# Login / Register / Logout / Profile
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash(
                "Please enter username and password.",
                "error"
            )
            return render_template("login.html")

        connection = None
        cursor = None

        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT id, username, email, password, role, student_id
                FROM users
                WHERE username = %s OR email = %s
                """,
                (username, username)
            )

            user = cursor.fetchone()

            if user and check_password_hash(
                user["password"],
                password
            ):

                # ---------------------------------------------
                # Store user information in session
                # ---------------------------------------------

                session["user_id"] = user.get("id")
                session["username"] = user["username"]
                session["email"] = user["email"]
                session["role"] = user["role"]
                session["student_id"] = user.get("student_id")

                flash(
                    "Login successful.",
                    "success"
                )

                return redirect(
                    url_for("home")
                )

            flash(
                "Invalid username or password.",
                "error"
            )

        except Exception as e:

            print(
                "Login database error:",
                e
            )

            flash(
                "Unable to connect to the database.",
                "error"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template("login.html")


# =========================================================
# Register
# =========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # -------------------------------------------------
        # Public registration role
        # -------------------------------------------------
        # Anyone registering through this page becomes
        # a STUDENT.
        #
        # FACULTY, PRINCIPAL and ADMIN accounts should
        # not be created through public registration.
        # -------------------------------------------------

        role = "STUDENT"

        # -------------------------------------------------
        # Basic validation
        # -------------------------------------------------

        if not username or not email or not password:

            flash(
                "Please fill in all required fields.",
                "error"
            )

            return render_template(
                "register.html"
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "register.html"
            )

        # -------------------------------------------------
        # Connect to database
        # -------------------------------------------------

        connection = None
        cursor = None

        try:

            connection = get_db_connection()

            cursor = connection.cursor(dictionary=True)

            # -------------------------------------------------
            # Check whether username already exists
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT username
                FROM users
                WHERE username = %s
                """,
                (username,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "Username already exists.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            # -------------------------------------------------
            # Check whether email already exists
            # -------------------------------------------------

            cursor.execute(
                """
                SELECT email
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing_email = cursor.fetchone()

            if existing_email:

                flash(
                    "Email already exists.",
                    "error"
                )

                return render_template(
                    "register.html"
                )

            # -------------------------------------------------
            # Hash password
            # -------------------------------------------------

            hashed_password = generate_password_hash(
                password
            )

            # -------------------------------------------------
            # Insert user with role
            # -------------------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    username,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    username,
                    email,
                    hashed_password,
                    role
                )
            )

            connection.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Exception as e:

            if connection:
                connection.rollback()

            print(
                "Registration database error:",
                e
            )

            flash(
                "Unable to register user.",
                "error"
            )

            return render_template(
                "register.html"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    return render_template(
        "register.html"
    )

# =========================================================
# Logout
# =========================================================

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# =========================================================
# Profile
# =========================================================

@app.route("/profile")
@login_required
def profile():

    if not session.get("username"):

        flash(
            "Please login first.",
            "error"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "profile.html",
        username=session.get("username"),
        email=session.get("email")
    )

# =========================================================
# 404 Page Not Found Handler
# =========================================================

@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404

# =========================================================
# 403 Forbidden Handler
# =========================================================

@app.errorhandler(403)
def forbidden(error):
    return render_template("403.html"), 403

# =========================================================
# 500 Internal Server Error Handler
# =========================================================

@app.errorhandler(500)
def internal_server_error(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug=True)