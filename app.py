import os
import joblib
import pandas as pd
import streamlit as st
import mysql.connector
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# Secure Configuration
# -----------------------------
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

if not all([DB_HOST, DB_USER, DB_PASSWORD, DB_NAME]):
    st.error("Database configuration missing.")
    st.stop()

# -----------------------------
# Database Connection Pool
# -----------------------------
try:
    db_pool = pooling.MySQLConnectionPool(
        pool_name="workshop_pool",
        pool_size=5,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
except mysql.connector.Error:
    st.error("Database initialization failed.")
    st.stop()


def get_connection():
    try:
        return db_pool.get_connection()
    except mysql.connector.Error:
        st.error("Database unavailable.")
        return None


# -----------------------------
# Load ML Model
# -----------------------------
@st.cache_resource
def load_model():
    try:
        return joblib.load("student_risk_model.pkl")
    except Exception:
        st.error("Model loading failed.")
        return None


model = load_model()


# -----------------------------
# Database Queries
# -----------------------------
def fetch_team_data(team_name):

    if not isinstance(team_name, str):
        return pd.DataFrame()

    conn = get_connection()
    if not conn:
        return pd.DataFrame()

    query = """
    SELECT student_name,
           classes_attended,
           homework_score_avg,
           assignments_completed,
           homework_count,
           homework_marks,
           project_count,
           project_marks,
           assignment_marks
    FROM Students
    WHERE team_id = (
        SELECT team_id FROM Teams WHERE team_name = %s
    )
    """

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (team_name,))
        rows = cursor.fetchall()
        return pd.DataFrame(rows)

    except mysql.connector.Error:
        return pd.DataFrame()

    finally:
        conn.close()


def update_student_record(data):

    required_fields = [
        "name","att","hw_c","hw_m","pr_c","pr_m","as_c","as_m"
    ]

    if not all(field in data for field in required_fields):
        return False

    conn = get_connection()
    if not conn:
        return False

    query = """
    UPDATE Students
    SET classes_attended=%s,
        homework_count=%s,
        homework_marks=%s,
        project_count=%s,
        project_marks=%s,
        assignments_completed=%s,
        assignment_marks=%s
    WHERE student_name=%s
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query, (
            int(data["att"]),
            int(data["hw_c"]),
            float(data["hw_m"]),
            int(data["pr_c"]),
            float(data["pr_m"]),
            int(data["as_c"]),
            float(data["as_m"]),
            data["name"]
        ))
        conn.commit()
        return True

    except mysql.connector.Error:
        return False

    finally:
        conn.close()


# -----------------------------
# Feature Engineering
# -----------------------------
def build_features(df, total_classes):

    if total_classes <= 0:
        return None

    df["combined_score"] = (
        df["homework_marks"] +
        df["project_marks"] +
        df["assignment_marks"]
    ) / 3

    df["attendance_scaled"] = (
        df["classes_attended"] / total_classes
    ) * 50

    return pd.DataFrame({
        "classes_attended": df["attendance_scaled"],
        "homework_score_avg": df["combined_score"] * 10,
        "assignments_completed": df["assignments_completed"]
    })


# -----------------------------
# Streamlit UI
# -----------------------------
def main():

    st.set_page_config(page_title="Workshop Tracker", layout="wide")
    st.title("Workshop ML Progress Tracker")

    teams = [
        "Team Daksh","Team Saksham","Team Sanjana",
        "Team Priyanjal","Team Hina","Team Chaman",
        "Team Tarun","Team Jiya"
    ]

    selected_team = st.sidebar.selectbox("Select Team", teams)

    df = fetch_team_data(selected_team)

    if df.empty:
        st.warning("No data available.")
        return

    total_classes = 5

    features = build_features(df, total_classes)

    if model and features is not None:

        try:
            preds = model.predict(features)
            df["AI_Status"] = [
                "At Risk" if p == 1 else "On Track"
                for p in preds
            ]
        except Exception:
            df["AI_Status"] = "Unknown"

    st.subheader("Student Overview")

    st.dataframe(
        df[[
            "student_name",
            "classes_attended",
            "assignments_completed",
            "AI_Status"
        ]],
        use_container_width=True
    )

    st.bar_chart(
        df.set_index("student_name")[[
            "classes_attended",
            "assignments_completed"
        ]]
    )


if __name__ == "__main__":
    main()