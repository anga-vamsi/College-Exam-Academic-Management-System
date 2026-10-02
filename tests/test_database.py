from db import get_db_connection


def test_database_connection():
    connection = get_db_connection()

    assert connection.is_connected()

    connection.close()