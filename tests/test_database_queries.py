from db import get_db_connection


def test_database_tables():
    connection = get_db_connection()
    cursor = connection.cursor()

    tables = [
        "Department",
        "Course",
        "Student",
        "Faculty",
        "Subject",
        "Exam",
        "Exam_Schedule",
        "Marks",
        "Attendance",
        "Result"
    ]

    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        result = cursor.fetchone()

        assert result[0] >= 0

    cursor.close()
    connection.close()