def test_student_result_trend(client):
    response = client.get("/student-result-trend")
    assert response.status_code == 200


def test_subject_student_count(client):
    response = client.get("/subject-student-count")
    assert response.status_code == 200


def test_exam_subject_summary(client):
    response = client.get("/exam-subject-summary")
    assert response.status_code == 200


def test_faculty_course_allocation(client):
    response = client.get("/faculty-course-allocation")
    assert response.status_code == 200


def test_course_faculty_count(client):
    response = client.get("/course-faculty-count")
    assert response.status_code == 200


def test_course_subject_count(client):
    response = client.get("/course-subject-count")
    assert response.status_code == 200


def test_exam_student_count(client):
    response = client.get("/exam-student-count")
    assert response.status_code == 200