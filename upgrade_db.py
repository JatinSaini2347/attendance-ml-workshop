import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "workshop_attendance")


COLUMNS_TO_ADD = {
    "homework_count": "INT DEFAULT 0",
    "homework_marks": "FLOAT DEFAULT 0.0",
    "project_count": "INT DEFAULT 0",
    "project_marks": "FLOAT DEFAULT 0.0",
    "assignment_marks": "FLOAT DEFAULT 0.0"
}


def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error:
        raise RuntimeError("Database connection failed")


def column_exists(cursor, column_name):

    query = """
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.COLUMNS
    WHERE TABLE_SCHEMA=%s
    AND TABLE_NAME='Students'
    AND COLUMN_NAME=%s
    """

    cursor.execute(query, (DB_NAME, column_name))
    result = cursor.fetchone()[0]

    return result > 0


def upgrade_schema():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        print("Starting database schema upgrade...")

        for column, definition in COLUMNS_TO_ADD.items():

            if column_exists(cursor, column):
                print(f"Skipping existing column: {column}")
                continue

            sql = f"ALTER TABLE Students ADD COLUMN {column} {definition}"
            cursor.execute(sql)

            print(f"Added column: {column}")

        conn.commit()

        print("Schema upgrade completed successfully")

    except Error as e:

        print("Schema upgrade failed:", str(e))

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    upgrade_schema()