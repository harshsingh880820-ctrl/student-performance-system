# Student Performance Analysis & Prediction System

A beginner-friendly full-stack college project using:
- Frontend: HTML, CSS, JavaScript
- Backend: Python Flask
- Database: SQLite
- Visualization: Chart.js
- Prediction: Weighted performance scoring algorithm

## How to run

1. Install Python 3.
2. Open this project folder in VS Code.
3. Open Terminal.
4. Run:

   pip install -r requirements.txt

5. Start the server:

   python app.py

6. Open the address shown in terminal, usually:

   http://127.0.0.1:5000

The database `students.db` is created automatically.

## Main modules

- Student registration/data entry
- Academic performance calculation
- Grade prediction
- Performance status
- Recommendations
- Dashboard
- Search students
- Student detail report
- Delete student
- JSON API at /api/students

## Prediction formula

Performance =
Attendance 20% +
Assignment 15% +
Internal Marks 25% +
Previous Marks 25% +
Study Hours 15%

This is a project-level prediction algorithm, not a certified academic grading system.
