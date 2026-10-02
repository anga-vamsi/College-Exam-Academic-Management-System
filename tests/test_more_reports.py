def test_top_students_report(client):
    response = client.get("/top-students-report")
    assert response.status_code == 200


def test_failed_students_report(client):
    response = client.get("/failed-students-report")
    assert response.status_code == 200


def test_passed_students_report(client):
    response = client.get("/passed-students-report")
    assert response.status_code == 200


def test_department_result_summary(client):
    response = client.get("/department-result-summary")
    assert response.status_code == 200


def test_course_result_comparison(client):
    response = client.get("/course-result-comparison")
    assert response.status_code == 200


def test_course_pass_fail_summary(client):
    response = client.get("/course-pass-fail-summary")
    assert response.status_code == 200


def test_student_pass_fail_summary(client):
    response = client.get("/student-pass-fail-summary")
    assert response.status_code == 200


def test_student_result_history(client):
    response = client.get("/student-result-history")
    assert response.status_code == 200