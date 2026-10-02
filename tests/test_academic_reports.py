def test_exam_student_performance(client):
    response = client.get("/exam-student-performance")
    assert response.status_code == 200


def test_faculty_subject_allocation(client):
    response = client.get("/faculty-subject-allocation")
    assert response.status_code == 200


def test_department_subject_summary(client):
    response = client.get("/department-subject-summary")
    assert response.status_code == 200


def test_course_student_count(client):
    response = client.get("/course-student-count")
    assert response.status_code == 200


def test_semester_subject_report(client):
    response = client.get("/semester-subject-report")
    assert response.status_code == 200


def test_student_attendance_summary(client):
    response = client.get("/student-attendance-summary")
    assert response.status_code == 200


def test_faculty_subject_count(client):
    response = client.get("/faculty-subject-count")
    assert response.status_code == 200


def test_department_faculty_count(client):
    response = client.get("/department-faculty-count")
    assert response.status_code == 200