def test_department_performance_report(client):
    response = client.get("/department-performance-report")
    assert response.status_code == 200


def test_subject_performance_report(client):
    response = client.get("/subject-performance-report")
    assert response.status_code == 200


def test_faculty_workload_report(client):
    response = client.get("/faculty-workload-report")
    assert response.status_code == 200


def test_student_rank_report(client):
    response = client.get("/student-rank-report")
    assert response.status_code == 200


def test_exam_result_summary(client):
    response = client.get("/exam-result-summary")
    assert response.status_code == 200


def test_attendance_defaulters(client):
    response = client.get("/attendance-defaulters")
    assert response.status_code == 200


def test_course_attendance_summary(client):
    response = client.get("/course-attendance-summary")
    assert response.status_code == 200


def test_student_marks_detail(client):
    response = client.get("/student-marks-detail")
    assert response.status_code == 200