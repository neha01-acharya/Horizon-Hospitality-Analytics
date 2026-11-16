
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()

# MySQL connection settings
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "neha",
    "password": os.getenv("MYSQL_PASSWORD", ""),
    "database": "horizon_hospitality_full",
}

def get_connection(include_database=True):
    """Create and return a MySQL database connection."""

    config = DB_CONFIG.copy()

    if not include_database:
        config.pop("database")

    try:
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print("MySQL connection successful!")

        return connection

    except Error as error:
        raise RuntimeError(
            f"MySQL connection failed: {error}"
        ) from error
