def test_student_performance(client):
    response = client.get("/student-performance/1")
    assert response.status_code == 200


def test_student_attendance(client):
    response = client.get("/student-attendance/1")
    assert response.status_code == 200


def test_student_dashboard(client):
    response = client.get("/student-dashboard/1")
    assert response.status_code == 200