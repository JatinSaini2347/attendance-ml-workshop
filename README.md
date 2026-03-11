# Workshop ML Attendance & Risk Prediction System

## Overview

This project is a **data-driven workshop monitoring system** that tracks student attendance, homework performance, and assignment completion to identify students who may be **at academic risk**.

It combines:

* **MySQL** for data storage
* **Python** for data processing
* **Scikit-learn** for machine learning
* **Streamlit** for the interactive dashboard

The system automatically analyzes student activity and predicts whether a student is **On Track** or **At Risk**.

---

## Project Architecture

```
CSV Dataset Generator
        │
        ▼
MySQL Database (Students + Teams)
        │
        ▼
ML Model Training (RandomForest)
        │
        ▼
Saved Model (.pkl)
        │
        ▼
Streamlit Dashboard
        │
        ▼
Live Student Monitoring
```

---

## Features

### Student Data Management

* Stores workshop student data in **MySQL**
* Team-based student organization
* Tracks:

  * Attendance
  * Homework scores
  * Assignment completion
  * Project performance

### Machine Learning Prediction

* RandomForest model predicts student risk level
* Uses features:

  * Classes attended
  * Homework score average
  * Assignments completed

### Interactive Dashboard

Built with **Streamlit**.

Features include:

* Team performance overview
* Individual student analytics
* Attendance vs performance visualization
* AI risk status detection
* Live student record updates

### Database Migration

Scripts allow schema upgrades such as adding:

* Homework marks
* Project marks
* Assignment marks

---

## Project Structure

```
project-root/
│
├── data_generator.py
│   Generates synthetic workshop student data
│
├── setup_database.py
│   Creates MySQL database and loads CSV data
│
├── train_model.py
│   Trains the ML risk prediction model
│
├── upgrade_database.py
│   Adds new columns to the Students table
│
├── app.py
│   Streamlit dashboard application
│
├── student_risk_model.pkl
│   Trained ML model
│
├── workshop_students_ml_data.csv
│   Generated dataset
│
└── README.md
```

---

## Database Schema

### Teams Table

| Column    | Type              |
| --------- | ----------------- |
| team_id   | INT (Primary Key) |
| team_name | VARCHAR           |

### Students Table

| Column                | Type    |
| --------------------- | ------- |
| student_id            | INT     |
| student_name          | VARCHAR |
| team_id               | INT     |
| total_classes         | INT     |
| classes_attended      | INT     |
| homework_score_avg    | FLOAT   |
| assignments_completed | INT     |
| homework_count        | INT     |
| homework_marks        | FLOAT   |
| project_count         | INT     |
| project_marks         | FLOAT   |
| assignment_marks      | FLOAT   |

---

## Installation

### 1. Clone the Repository

```
git clone https://github.com/yourusername/workshop-ml-tracker.git
cd workshop-ml-tracker
```

### 2. Install Dependencies

```
pip install -r requirements.txt
```

Example dependencies:

```
pandas
mysql-connector-python
scikit-learn
streamlit
joblib
python-dotenv
```

---

## Environment Configuration

Create a `.env` file:

```
DB_HOST=localhost
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=workshop_attendance
```

---

## Usage

### Step 1 — Generate Dataset

```
python data_generator.py
```

Creates:

```
workshop_students_ml_data.csv
```

---

### Step 2 — Create Database and Insert Data

```
python setup_database.py
```

Creates:

* MySQL database
* Teams table
* Students table
* Inserts student records

---

### Step 3 — Train Machine Learning Model

```
python train_model.py
```

Outputs:

```
student_risk_model.pkl
```

---

### Step 4 — Launch Dashboard

```
streamlit run app.py
```

Open browser:

```
http://localhost:8501
```

---

## Machine Learning Model

**Algorithm**

```
RandomForestClassifier
```

**Input Features**

* classes_attended
* homework_score_avg
* assignments_completed

**Target**

```
is_at_risk
```

Rule used to label data:

```
At Risk if:
    classes_attended < 35
    OR
    homework_score_avg < 60
```

---

## Security Considerations

The secure version of the project includes:

* Environment variable credentials
* Parameterized SQL queries
* Input validation
* Safe database connection handling
* Restricted database roles
* Controlled schema migrations

---

## Future Improvements

* Authentication system for dashboard access
* Role-based admin panel
* Real-time attendance tracking
* Model versioning (MLflow)
* Docker containerization
* CI/CD deployment
* Advanced risk prediction models

---

## License

This project is provided for **educational and research purposes**.

---

## Author

Machine Learning & Data Engineering Project
Workshop Attendance Monitoring System
