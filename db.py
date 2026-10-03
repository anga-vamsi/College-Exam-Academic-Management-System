import os
import mysql.connector

from config import Config


def get_db_connection():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        ssl_disabled=False
    )

    return connection