import mysql.connector

# Connect to your database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='Pablo$100',
    database='workshop_attendance'
)
cursor = conn.cursor()

# Add the new specific columns
new_columns = [
    "ALTER TABLE Students ADD COLUMN homework_count INT DEFAULT 0;",
    "ALTER TABLE Students ADD COLUMN homework_marks FLOAT DEFAULT 0.0;",
    "ALTER TABLE Students ADD COLUMN project_count INT DEFAULT 0;",
    "ALTER TABLE Students ADD COLUMN project_marks FLOAT DEFAULT 0.0;",
    "ALTER TABLE Students ADD COLUMN assignment_marks FLOAT DEFAULT 0.0;"
]

print("Upgrading database schema...")
for sql in new_columns:
    try:
        cursor.execute(sql)
    except mysql.connector.Error as err:
        print(f"Skipping (column might already exist): {err}")

conn.commit()
conn.close()
print("Database successfully upgraded! You can delete this script.")