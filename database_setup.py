import mysql.connector
import pandas as pd
from mysql.connector import Error

def setup_mysql_database(csv_filename):
    try:
        # 1. Connect to your local MySQL Server
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Pablo$100' 
        )
        cursor = connection.cursor()

        # 2. Create the Database
        cursor.execute("CREATE DATABASE IF NOT EXISTS workshop_attendance;")
        cursor.execute("USE workshop_attendance;")
        print("Database 'workshop_attendance' ready.")

        # 3. Create the Normalized Tables
        create_teams_table = """
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INT AUTO_INCREMENT PRIMARY KEY,
            team_name VARCHAR(255) UNIQUE NOT NULL
        );
        """
        create_students_table = """
        CREATE TABLE IF NOT EXISTS Students (
            student_id INT PRIMARY KEY,
            student_name VARCHAR(255) NOT NULL,
            team_id INT,
            total_classes INT,
            classes_attended INT,
            homework_score_avg FLOAT,
            assignments_completed INT,
            FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        );
        """
        cursor.execute(create_teams_table)
        cursor.execute(create_students_table)
        print("Tables 'Teams' and 'Students' created.")

        # 4. Read the generated CSV data
        df = pd.read_csv(csv_filename)

        # 5. Insert the 8 Teams First
        unique_teams = df['team_name'].unique()
        for team in unique_teams:
            cursor.execute("INSERT IGNORE INTO Teams (team_name) VALUES (%s)", (team,))
        connection.commit()

        # Fetch the auto-generated team IDs to link to the students
        cursor.execute("SELECT team_id, team_name FROM Teams;")
        team_mapping = {name: id for id, name in cursor.fetchall()}

        # 6. Insert the 40 Students
        insert_student_query = """
        INSERT IGNORE INTO Students (
            student_id, student_name, team_id, total_classes, 
            classes_attended, homework_score_avg, assignments_completed
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        for index, row in df.iterrows():
            current_team_id = team_mapping[row['team_name']]
            
            student_data = (
                row['student_id'],
                row['student_name'],
                current_team_id,
                row['total_classes'],
                row['classes_attended'],
                row['homework_score_avg'],
                row['assignments_completed']
            )
            cursor.execute(insert_student_query, student_data)
            
        connection.commit()
        print(f"Successfully inserted {len(df)} student records into the MySQL database!")

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    setup_mysql_database('workshop_students_ml_data.csv')