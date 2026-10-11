from flask import Flask, render_template, request, redirect, url_for, jsonify
from ml_model import predict_performance
import sqlite3
from flask import make_response
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

app = Flask(__name__)
DB = "students.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            course TEXT NOT NULL,
            semester INTEGER NOT NULL,
            attendance REAL NOT NULL,
            assignment REAL NOT NULL,
            internal_marks REAL NOT NULL,
            previous_marks REAL NOT NULL,
            study_hours REAL NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def predict(attendance, assignment, internal, previous, study):

    score = predict_performance(
        attendance,
        assignment,
        internal,
        previous,
        study
    )

    if score >= 85:
        grade = "A+"
        status = "Excellent"
    elif score >= 75:
        grade = "A"
        status = "Very Good"
    elif score >= 65:
        grade = "B"
        status = "Good"
    elif score >= 50:
        grade = "C"
        status = "Average"
    elif score >= 40:
        grade = "D"
        status = "Needs Improvement"
    else:
        grade = "F"
        status = "At Risk"

    # Pass / Fail
    score=float(score)
    
    if score >= 40:
        result = "PASS"
    else:
        result = "FAIL"

    recommendations = []

    if attendance < 75:
        recommendations.append("Improve attendance to at least 75%.")

    if assignment < 60:
        recommendations.append("Submit assignments regularly.")

    if internal < 60:
        recommendations.append("Practice more for internal tests.")

    if previous < 60:
        recommendations.append("Revise previous topics.")

    if study < 2:
        recommendations.append("Increase daily study time.")

    if not recommendations:
        recommendations.append("Keep up the good work!")

    return score, grade, status, recommendations, result

@app.route("/")
def index():
    conn = get_db()
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    avg = conn.execute("""
        SELECT AVG(
            attendance * 0.20 +
            assignment * 0.15 +
            internal_marks * 0.25 +
            previous_marks * 0.25 +
            MIN(study_hours / 8 * 100, 100) * 0.15
        ) FROM students
    """).fetchone()[0] or 0

    conn.close()

    student_data = []

    for s in students:
        score, grade, status, rec, result = predict(
            s["attendance"],
            s["assignment"],
            s["internal_marks"],
            s["previous_marks"],
            s["study_hours"]
        )
        result="PASS"if float(score) >=40 else "FAIL"

        student_data.append({
            "id": s["id"],
            "name": s["name"],
            "roll_no": s["roll_no"],
            "course": s["course"],
            "semester": s["semester"],
            "score": score,
            "grade": grade,
            "status": status,
            "result": result
        })

    pass_count = sum(1 for student in student_data if student["result"] == "PASS")
    fail_count = sum(1 for student in student_data if student["result"] == "FAIL")
    top_students = sorted(
        student_data, key=lambda student: student["score"], reverse=True
    )[:5]

    return render_template(
        "index.html",
        students=student_data,
        total=total,
        average=round(avg, 2),
        pass_count=pass_count,
        fail_count=fail_count,
        top_students=top_students
    )

@app.route("/add", methods=["POST"])
def add_student():
    data = request.form
    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO students
            (name, roll_no, course, semester, attendance, assignment,
             internal_marks, previous_marks, study_hours, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"].strip(), data["roll_no"].strip(), data["course"].strip(),
            int(data["semester"]), float(data["attendance"]),
            float(data["assignment"]), float(data["internal_marks"]),
            float(data["previous_marks"]), float(data["study_hours"]),
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return "Error: Roll number already exists. <a href='/'>Go back</a>", 400
    return redirect(url_for("index"))

@app.route("/student/<int:student_id>")
def student_detail(student_id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    conn.close()
    if not student:
        return "Student not found", 404

    score, grade, status, recommendations, result = predict(
        student["attendance"], student["assignment"],
        student["internal_marks"], student["previous_marks"],
        student["study_hours"]
    )
    return render_template("student.html", student=student, score=score,
                           grade=grade, status=status,
                           recommendations=recommendations,result=result)

@app.route("/delete/<int:student_id>", methods=["POST"])
def delete_student(student_id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/api/students")
def api_students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    students = []
    for s in rows:
        score, grade, status, _, pass_fail_result = predict(
            s["attendance"], s["assignment"], s["internal_marks"],
            s["previous_marks"], s["study_hours"]
        )
        students.append({
            "id": s["id"], "name": s["name"], "roll_no": s["roll_no"],
            "score": score, "grade": grade, "status": status,
            "result": pass_fail_result
        })
    return jsonify(students)

@app.route("/student/<int:student_id>/pdf")
def student_pdf(student_id):
    conn = get_db()
    student = conn.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()
    conn.close()

    if not student:
        return "Student not found", 404

    score, grade, status, recommendations, result = predict(
        student["attendance"],
        student["assignment"],
        student["internal_marks"],
        student["previous_marks"],
        student["study_hours"]
    )

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setTitle("Student Performance Report")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(60, 780, "Student Performance Report")

    pdf.setFont("Helvetica", 12)
    lines = [
        f"Name: {student['name']}",
        f"Roll Number: {student['roll_no']}",
        f"Course: {student['course']}",
        f"Semester: {student['semester']}",
        f"Attendance: {student['attendance']}%",
        f"Assignment: {student['assignment']}%",
        f"Internal Marks: {student['internal_marks']}%",
        f"Previous Marks: {student['previous_marks']}%",
        f"Study Hours: {student['study_hours']} per day",
        f"Predicted Performance: {score}%",
        f"Grade: {grade}",
        f"Status: {status}",
        f"Result: {result}",
    ]

    y = 735
    for line in lines:
        pdf.drawString(60, y, line)
        y -= 30

    pdf.save()
    buffer.seek(0)

    response = make_response(buffer.getvalue())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = (
        f'attachment; filename="student_{student_id}_report.pdf"'
    )
    return response

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
