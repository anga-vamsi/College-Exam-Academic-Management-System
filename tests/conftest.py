import pytest

from app import app


@pytest.fixture
def client():
    app.config.update(
        TESTING=True,
        WTF_CSRF_ENABLED=False,
        SESSION_COOKIE_SECURE=False,
    )

    with app.test_client() as client:
        with client.session_transaction() as session:
            session["user_id"] = 1
            session["username"] = "admin"
            session["email"] = "admin@gmail.com"
            session["role"] = "ADMIN"
            session["student_id"] = None
            session["_csrf_token"] = "test-csrf-token"

        yield client