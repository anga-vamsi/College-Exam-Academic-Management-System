def test_exam_schedule_course_report(client):
    response = client.get("/exam-schedule-course-report")
    assert response.status_code == 200


def test_student_exam_schedule(client):
    response = client.get("/student-exam-schedule")
    assert response.status_code == 200


def test_student_subject_performance(client):
    response = client.get("/student-subject-performance")
    assert response.status_code == 200


def test_subject_marks_summary(client):
    response = client.get("/subject-marks-summary")
    assert response.status_code == 200


def test_department_attendance_summary(client):
    response = client.get("/department-attendance-summary")
    assert response.status_code == 200


def test_department_academic_overview(client):
    response = client.get("/department-academic-overview")
    assert response.status_code == 200


def test_department_student_performance(client):
    response = client.get("/department-student-performance")
    assert response.status_code == 200


def test_student_academic_overview(client):
    response = client.get("/student-academic-overview")
    assert response.status_code == 200