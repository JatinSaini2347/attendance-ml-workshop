import pandas as pd
import random

def generate_workshop_data():
    # Your official 8 teams
    team_rosters = {
        "Team Daksh": ["Daksh", "Vaibhav", "Shushant", "Bhavishya", "Vansh"],
        "Team Saksham": ["Saksham", "Aryan Dhaiya", "Alok Raj", "Krrish", "Manjeet"],
        "Team Sanjana": ["Sanjana", "Kajal", "Preet", "Bharat", "Samar"],
        "Team Priyanjal": ["Priyanjal", "Ahana", "Dristi", "Disha", "Manshika"],
        "Team Hina": ["Hina", "Jiya", "Mitali", "Jatin", "Anuj Kumar"],
        "Team Chaman": ["Chaman", "Alok Yadav", "Anshuman", "Ankita Rai", "Muskan"],
        "Team Tarun": ["Tarun", "Naman", "Harsh", "Yash", "Nishant"],
        "Team Jiya": ["Jiya", "Khushboo", "Vanshika", "Kanishka", ],
    }

    students_data = []
    student_id = 1
    total_classes = 50

    for team_name, members in team_rosters.items():
        for student_name in members:
            # Randomize a "student profile" to create realistic ML data
            # 0: Struggling, 1: Average, 2: High Achiever
            profile = random.choices([0, 1, 2], weights=[0.2, 0.5, 0.3])[0]
            
            if profile == 0:
                classes_attended = random.randint(20, 35)
                noise = random.uniform(-10, 10)
            elif profile == 1:
                classes_attended = random.randint(35, 45)
                noise = random.uniform(-5, 5)
            else:
                classes_attended = random.randint(45, 50)
                noise = random.uniform(-2, 2)
                
            attendance_rate = classes_attended / total_classes
            
            # Homework and assignments correlate with attendance
            homework_score_avg = round(min(max((attendance_rate * 100) + noise, 40.0), 100.0), 2)
            assignments_completed = int(min(max((attendance_rate * 10) + random.randint(-1, 1), 0), 10))

            students_data.append({
                'student_id': student_id,
                'student_name': student_name,
                'team_name': team_name,
                'total_classes': total_classes,
                'classes_attended': classes_attended,
                'homework_score_avg': homework_score_avg,
                'assignments_completed': assignments_completed
            })
            student_id += 1

    return pd.DataFrame(students_data)

if __name__ == "__main__":
    print("Generating student data...")
    df_students = generate_workshop_data()
    
    # Export to CSV
    file_name = "workshop_students_ml_data.csv"
    df_students.to_csv(file_name, index=False)
    
    print(f"Success! 40 student records saved to '{file_name}'.")
    print("\nHere is a quick preview of your data:")
    print(df_students.head())