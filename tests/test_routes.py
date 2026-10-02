def test_students_page(client):
    response = client.get("/students")
    assert response.status_code == 200


def test_faculty_page(client):
    response = client.get("/faculty")
    assert response.status_code == 200


def test_courses_page(client):
    response = client.get("/courses")
    assert response.status_code == 200


def test_subjects_page(client):
    response = client.get("/subjects")
    assert response.status_code == 200


def test_exams_page(client):
    response = client.get("/exams")
    assert response.status_code == 200


def test_results_page(client):
    response = client.get("/results")
    assert response.status_code == 200


def test_attendance_page(client):
    response = client.get("/attendance")
    assert response.status_code == 200