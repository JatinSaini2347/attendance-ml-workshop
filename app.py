import streamlit as st
import pandas as pd
import mysql.connector
import joblib
import os
from dotenv import load_dotenv 

# Load the hidden vault
load_dotenv()
MY_SECURE_PASSWORD = os.getenv("DB_PASSWORD")

# 1. Load the AI Model
model = joblib.load('student_risk_model.pkl')

# 2. Function to fetch data from MySQL
def fetch_team_data(team_name):
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password=MY_SECURE_PASSWORD, 
        database='workshop_attendance'
    )
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT s.student_name, s.classes_attended, s.homework_score_avg, 
               s.assignments_completed, s.homework_count, s.homework_marks, 
               s.project_count, s.project_marks, s.assignment_marks
        FROM Students s
        JOIN Teams t ON s.team_id = t.team_id
        WHERE t.team_name = %s
    """
    cursor.execute(query, (team_name,))
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data)

# 3. Function to update an individual student
def update_student_record(name, att, hw_c, hw_m, pr_c, pr_m, as_c, as_m):
    conn = mysql.connector.connect(
        host='localhost', 
        user='root', 
        password=MY_SECURE_PASSWORD,
        database='workshop_attendance' 
    )
    cursor = conn.cursor()
    query = """
        UPDATE Students 
        SET classes_attended=%s, homework_count=%s, homework_marks=%s, 
            project_count=%s, project_marks=%s, assignments_completed=%s, assignment_marks=%s
        WHERE student_name=%s
    """
    cursor.execute(query, (int(att), int(hw_c), float(hw_m), int(pr_c), float(pr_m), int(as_c), float(as_m), name))
    conn.commit()
    conn.close()

# 4. NEW: Functions to get and update the Total Classes globally
def get_global_total_classes():
    conn = mysql.connector.connect(
        host='localhost', user='root', password=MY_SECURE_PASSWORD, database='workshop_attendance' # <-- 3rd PASSWORD TO UPDATE
    )
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(total_classes) FROM Students")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result else 5

def update_global_total_classes(new_total):
    conn = mysql.connector.connect(
        host='localhost', user='root', password=MY_SECURE_PASSWORD, database='workshop_attendance' # <-- 4th PASSWORD TO UPDATE (Sorry, there are 4 now!)
    )
    cursor = conn.cursor()
    # This updates the total_classes limit for everyone in the database permanently
    cursor.execute("UPDATE Students SET total_classes = %s", (int(new_total),))
    conn.commit()
    conn.close()

# --- BUILD THE USER INTERFACE ---
st.set_page_config(page_title="Workshop ML Tracker", layout="wide")
st.title("📊 ML Attendance & Progress Tracker")

# 5. NEW: Permanent Workshop Settings UI
st.sidebar.header("🎓 Workshop Settings")
current_total_classes = get_global_total_classes()

st.sidebar.write(f"**Current Total Classes Held:** {current_total_classes}")
with st.sidebar.form("update_total_classes_form"):
    new_total_input = st.number_input("Update Total Classes", min_value=1, value=int(current_total_classes), step=1)
    if st.form_submit_button("Save New Class Total"):
        update_global_total_classes(new_total_input)
        st.sidebar.success("Workshop total classes updated!")
        st.rerun()

st.sidebar.markdown("---")

# 6. Navigation
st.sidebar.header("Navigation")
teams = [
    "Team Daksh", "Team Saksham", "Team Sanjana", "Team Priyanjal", 
    "Team Hina", "Team Chaman", "Team Tarun", "Team Jiya"
]
selected_team = st.sidebar.selectbox("Select a Team to Analyze", teams)

st.header(f"Performance Report: {selected_team}")

# 7. Fetch the selected team's data
df = fetch_team_data(selected_team)

# 8. Build the Sidebar Form
st.sidebar.markdown("---")
st.sidebar.header("📝 Live Data Entry")

if not df.empty:
    student_list = df['student_name'].tolist()
    selected_update_student = st.sidebar.selectbox("Select Student to Update", student_list)
    current_stats = df[df['student_name'] == selected_update_student].iloc[0]
    
    with st.sidebar.form("update_form"):
        st.write(f"Updating: **{selected_update_student}**")
        
        # Max value uses the permanent database number
        safe_attendance = min(int(current_stats.get('classes_attended', 0)), int(current_total_classes))
        new_att = st.number_input("Classes Attended", min_value=0, max_value=int(current_total_classes), value=safe_attendance)
        
        st.markdown("**Homework**")
        col1, col2 = st.columns(2)
        new_hw_c = col1.number_input("Count (HW)", min_value=0, value=int(current_stats.get('homework_count', 0)), key="hw_count")
        new_hw_m = col2.number_input("Marks (/10)", min_value=0.0, max_value=10.0, value=float(current_stats.get('homework_marks', 0.0)), key="hw_marks")

        st.markdown("**Projects**")
        col3, col4 = st.columns(2)
        new_pr_c = col3.number_input("Count (Proj)", min_value=0, value=int(current_stats.get('project_count', 0)), key="proj_count")
        new_pr_m = col4.number_input("Marks (/10)", min_value=0.0, max_value=10.0, value=float(current_stats.get('project_marks', 0.0)), key="proj_marks")

        st.markdown("**Assignments**")
        col5, col6 = st.columns(2)
        new_as_c = col5.number_input("Count (Assign)", min_value=0, value=int(current_stats.get('assignments_completed', 0)), key="assign_count")
        new_as_m = col6.number_input("Marks (/10)", min_value=0.0, max_value=10.0, value=float(current_stats.get('assignment_marks', 0.0)), key="assign_marks")
        
        submitted = st.form_submit_button("Save to Database")
        
        if submitted:
            update_student_record(selected_update_student, new_att, new_hw_c, new_hw_m, new_pr_c, new_pr_m, new_as_c, new_as_m)
            st.sidebar.success(f"Updated {selected_update_student}!")
            st.rerun()

# 9. Render Main Dashboard and ML Predictions
if not df.empty:
    df['combined_avg_out_of_10'] = (df['homework_marks'] + df['project_marks'] + df['assignment_marks']) / 3
    df['homework_score_avg'] = df['combined_avg_out_of_10'] * 10 
    
    # Scale attendance using the permanent DB value
    df['scaled_attendance'] = (df['classes_attended'] / current_total_classes) * 50
    
    ai_features = pd.DataFrame({
        'classes_attended': df['scaled_attendance'],
        'homework_score_avg': df['homework_score_avg'],
        'assignments_completed': df['assignments_completed']
    })
    
    predictions = model.predict(ai_features)
    df['AI_Status'] = ['🔴 At Risk' if pred == 1 else '🟢 On Track' for pred in predictions]
    
    col1, col2 = st.columns(2)
    col1.metric("Team Average Attendance", f"{df['classes_attended'].mean():.1f} / {current_total_classes}")
    col2.metric("Team Avg (HW/Proj/Assign Combined)", f"{df['homework_score_avg'].mean():.1f}%")

    st.subheader("Individual Student Breakdown")
    st.dataframe(df[['student_name', 'classes_attended', 'homework_score_avg', 'AI_Status']], width='stretch')

    st.subheader("Attendance vs. Overall Scores")
    st.bar_chart(df.set_index('student_name')[['classes_attended', 'homework_score_avg']])
else:
    st.warning("No data found for this team. Check your database connection.")