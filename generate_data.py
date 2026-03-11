import pandas as pd
import secrets
import os

TOTAL_CLASSES = 50
OUTPUT_FILE = "workshop_students_ml_data.csv"

TEAM_ROSTERS = {
    "Team Daksh": ["Daksh","Vaibhav","Shushant","Bhavishya","Vansh"],
    "Team Saksham": ["Saksham","Aryan Dhaiya","Alok Raj","Krrish","Manjeet"],
    "Team Sanjana": ["Sanjana","Kajal","Preet","Bharat","Samar"],
    "Team Priyanjal": ["Priyanjal","Ahana","Dristi","Disha","Manshika"],
    "Team Hina": ["Hina","Jiya","Mitali","Jatin","Anuj Kumar"],
    "Team Chaman": ["Chaman","Alok Yadav","Anshuman","Ankita Rai","Muskan"],
    "Team Tarun": ["Tarun","Naman","Harsh","Yash","Nishant"],
    "Team Jiya": ["Jiya","Khushboo","Vanshika","Kanishka"]
}


def secure_randint(min_val, max_val):
    return min_val + secrets.randbelow(max_val - min_val + 1)


def secure_uniform(min_val, max_val):
    scale = 100
    rand = secrets.randbelow((max_val - min_val) * scale)
    return min_val + rand / scale


def generate_profile():
    # weighted selection
    r = secrets.randbelow(100)

    if r < 20:
        return 0
    elif r < 70:
        return 1
    return 2


def generate_workshop_data():

    students = []
    student_id = 1

    for team_name, members in TEAM_ROSTERS.items():

        if not isinstance(members, list):
            continue

        for student in members:

            if not isinstance(student, str) or not student.strip():
                continue

            profile = generate_profile()

            if profile == 0:
                classes_attended = secure_randint(20, 35)
                noise = secure_uniform(-10, 10)

            elif profile == 1:
                classes_attended = secure_randint(35, 45)
                noise = secure_uniform(-5, 5)

            else:
                classes_attended = secure_randint(45, 50)
                noise = secure_uniform(-2, 2)

            attendance_rate = classes_attended / TOTAL_CLASSES

            score = (attendance_rate * 100) + noise
            homework_score_avg = round(min(max(score, 40.0), 100.0), 2)

            assignments = (attendance_rate * 10) + secure_randint(-1, 1)
            assignments_completed = int(min(max(assignments, 0), 10))

            students.append({
                "student_id": student_id,
                "student_name": student.strip(),
                "team_name": team_name,
                "total_classes": TOTAL_CLASSES,
                "classes_attended": classes_attended,
                "homework_score_avg": homework_score_avg,
                "assignments_completed": assignments_completed
            })

            student_id += 1

    return pd.DataFrame(students)


def save_dataset(df):

    if df.empty:
        raise ValueError("Dataset is empty")

    if os.path.exists(OUTPUT_FILE):
        raise FileExistsError("Output file already exists")

    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":

    try:

        print("Generating workshop dataset...")

        dataset = generate_workshop_data()

        save_dataset(dataset)

        print(f"{len(dataset)} student records saved to {OUTPUT_FILE}")

        print("\nPreview:")
        print(dataset.head())

    except Exception as e:

        print("Dataset generation failed:", str(e))