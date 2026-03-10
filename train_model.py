import mysql.connector
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_attendance_model():
    # 1. Connect to MySQL and pull the data
    print("Fetching data from MySQL...")
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Pablo$100', 
        database='workshop_attendance'
    )
    
    query = """
    SELECT student_name, classes_attended, homework_score_avg, assignments_completed 
    FROM Students;
    """
    cursor = connection.cursor()
    cursor.execute(query)
    
    # Put the data into a Pandas DataFrame
    columns = [col[0] for col in cursor.description]
    df = pd.DataFrame(cursor.fetchall(), columns=columns)
    
    connection.close()
    
    # 2. Feature Engineering (Define who is "At Risk")
    # Rule: If attendance is < 35 OR homework < 60, they need intervention (1). Else, safe (0).
    print("Engineering target variables...")
    def determine_risk(row):
        if row['classes_attended'] < 35 or row['homework_score_avg'] < 60.0:
            return 1 # At Risk
        return 0 # Safe
        
    df['is_at_risk'] = df.apply(determine_risk, axis=1)
    
    # 3. Prepare Data for the ML Model
    # X = The features (inputs) | y = The target (output)
    X = df[['classes_attended', 'homework_score_avg', 'assignments_completed']]
    y = df['is_at_risk']
    
    # Split data: 80% to train the model, 20% to test its accuracy
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 4. Train the Model (Random Forest Classifier)
    print("Training the Machine Learning model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Evaluate the Model
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"\n--- Model Training Complete ---")
    print(f"Model Accuracy: {accuracy * 100:.2f}%")
    print("\nDetailed Report:")
    print(classification_report(y_test, predictions))
    
    # 6. Save the trained model to a file
    model_filename = "student_risk_model.pkl"
    joblib.dump(model, model_filename)
    print(f"Model successfully saved as '{model_filename}'.")

if __name__ == "__main__":
    train_attendance_model()