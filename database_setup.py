import os
import mysql.connector
import pandas as pd
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "workshop_attendance")

REQUIRED_COLUMNS = [
    "student_id",
    "student_name",
    "team_name",
    "total_classes",
    "classes_attended",
    "homework_score_avg",
    "assignments_completed"
]


def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
    except Error:
        raise RuntimeError("Database connection failed")


def validate_csv(df):
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in CSV: {missing}")

    if df.empty:
        raise ValueError("CSV file is empty")

    return df[REQUIRED_COLUMNS]


def create_schema(cursor):

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    cursor.execute(f"USE {DB_NAME}")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INT AUTO_INCREMENT PRIMARY KEY,
            team_name VARCHAR(255) UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Students (
            student_id INT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            team_id INT,
            total_classes INT,
            classes_attended INT,
            homework_score_avg FLOAT,
            assignments_completed INT,
            FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        )
    """)


def insert_teams(cursor, teams):

    query = "INSERT IGNORE INTO Teams (team_name) VALUES (%s)"

    for team in teams:
        if isinstance(team, str) and len(team) <= 255:
            cursor.execute(query, (team.strip(),))


def build_team_map(cursor):

    cursor.execute("SELECT team_id, team_name FROM Teams")

    mapping = {}
    for team_id, team_name in cursor.fetchall():
        mapping[team_name] = team_id

    return mapping


def insert_students(cursor, df, team_map):

    insert_query = """
        INSERT IGNORE INTO Students (
            student_id,
            student_name,
            team_id,
            total_classes,
            classes_attended,
            homework_score_avg,
            assignments_completed
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    for _, row in df.iterrows():

        team_id = team_map.get(row["team_name"])

        if not team_id:
            continue

        student_data = (
            int(row["student_id"]),
            str(row["student_name"]).strip(),
            int(team_id),
            int(row["total_classes"]),
            int(row["classes_attended"]),
            float(row["homework_score_avg"]),
            int(row["assignments_completed"])
        )

        cursor.execute(insert_query, student_data)


def setup_database(csv_file):

    if not os.path.exists(csv_file):
        raise FileNotFoundError("CSV file not found")

    df = pd.read_csv(csv_file)
    df = validate_csv(df)

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        create_schema(cursor)

        teams = df["team_name"].unique()
        insert_teams(cursor, teams)

        conn.commit()

        team_map = build_team_map(cursor)

        insert_students(cursor, df, team_map)

        conn.commit()

        print(f"{len(df)} records inserted successfully")

    except Exception as e:
        print("Operation failed:", str(e))

    finally:

        if cursor:
            cursor.close()

        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    setup_database("workshop_students_ml_data.csv")