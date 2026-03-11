import os
import mysql.connector
import pandas as pd
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME", "workshop_attendance")

MODEL_FILE = "student_risk_model.pkl"


def get_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except mysql.connector.Error:
        raise RuntimeError("Database connection failed")


def fetch_student_data():

    query = """
    SELECT
        classes_attended,
        homework_score_avg,
        assignments_completed
    FROM Students
    """

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(query)

        columns = [col[0] for col in cursor.description]
        df = pd.DataFrame(cursor.fetchall(), columns=columns)

        if df.empty:
            raise ValueError("No training data found")

        return df

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


def create_target_variable(df):

    if not all(col in df.columns for col in [
        "classes_attended",
        "homework_score_avg",
        "assignments_completed"
    ]):
        raise ValueError("Dataset schema invalid")

    def determine_risk(row):
        if row["classes_attended"] < 35 or row["homework_score_avg"] < 60:
            return 1
        return 0

    df["is_at_risk"] = df.apply(determine_risk, axis=1)

    return df


def train_model(df):

    X = df[[
        "classes_attended",
        "homework_score_avg",
        "assignments_completed"
    ]]

    y = df["is_at_risk"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    accuracy = accuracy_score(y_test, predictions)

    print(f"Model accuracy: {accuracy*100:.2f}%")
    print(classification_report(y_test, predictions))

    return model


def save_model(model):

    if os.path.exists(MODEL_FILE):
        raise FileExistsError("Model file already exists")

    joblib.dump(model, MODEL_FILE)


def main():

    try:

        print("Fetching training data...")
        df = fetch_student_data()

        print("Preparing dataset...")
        df = create_target_variable(df)

        print("Training model...")
        model = train_model(df)

        print("Saving model...")
        save_model(model)

        print("Training completed successfully")

    except Exception as e:
        print("Training failed:", str(e))


if __name__ == "__main__":
    main()