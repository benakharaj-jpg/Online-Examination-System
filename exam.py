import sqlite3
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
conn = sqlite3.connect("online_exam.db")
cursor = conn.cursor()

# Users table (students & instructors)
cursor.execute('''CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    role TEXT CHECK(role IN ('Student','Instructor'))
)''')

# Exams table
cursor.execute('''CREATE TABLE IF NOT EXISTS Exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    instructor_id INTEGER,
    total_marks INTEGER DEFAULT 0,
    date TEXT,
    FOREIGN KEY(instructor_id) REFERENCES Users(user_id)
)''')

# Questions table
cursor.execute('''CREATE TABLE IF NOT EXISTS Questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    question_text TEXT,
    option1 TEXT,
    option2 TEXT,
    option3 TEXT,
    option4 TEXT,
    correct_option INTEGER,
    marks INTEGER DEFAULT 1,
    FOREIGN KEY(exam_id) REFERENCES Exams(exam_id)
)''')

# Results table
cursor.execute('''CREATE TABLE IF NOT EXISTS Results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER,
    student_id INTEGER,
    score INTEGER,
    submitted_at TEXT,
    FOREIGN KEY(exam_id) REFERENCES Exams(exam_id),
    FOREIGN KEY(student_id) REFERENCES Users(user_id)
)''')

conn.commit()

# -----------------------------
# USER MANAGEMENT
# -----------------------------
def add_user():
    name = input("Enter Name: ")
    email = input("Enter Email: ")
    role = input("Enter Role (Student/Instructor): ")
    cursor.execute("INSERT INTO Users (name, email, role) VALUES (?, ?, ?)", (name, email, role))
    conn.commit()
    print("✅ User added")

def view_users():
    cursor.execute("SELECT * FROM Users")
    for row in cursor.fetchall():
        print(row)

def update_user():
    view_users()
    user_id = int(input("Enter User ID to update: "))
    name = input("Enter New Name: ")
    email = input("Enter New Email: ")
    role = input("Enter Role (Student/Instructor): ")
    cursor.execute("UPDATE Users SET name=?, email=?, role=? WHERE user_id=?", (name, email, role, user_id))
    conn.commit()
    print("✅ User updated")

def delete_user():
    view_users()
    user_id = int(input("Enter User ID to delete: "))
    cursor.execute("DELETE FROM Users WHERE user_id=?", (user_id,))
    conn.commit()
    print("✅ User deleted")

# -----------------------------
# EXAM MANAGEMENT
# -----------------------------
def create_exam():
    view_users()
    instructor_id = int(input("Enter Instructor ID for this exam: "))
    title = input("Enter Exam Title: ")
    date = input("Enter Exam Date (YYYY-MM-DD): ")
    cursor.execute("INSERT INTO Exams (title, instructor_id, date) VALUES (?, ?, ?)", (title, instructor_id, date))
    conn.commit()
    print("✅ Exam created")

def view_exams():
    cursor.execute('''SELECT e.exam_id, e.title, u.name, e.total_marks, e.date
                      FROM Exams e LEFT JOIN Users u ON e.instructor_id = u.user_id''')
    for row in cursor.fetchall():
        print(row)

def update_exam():
    view_exams()
    exam_id = int(input("Enter Exam ID to update: "))
    title = input("Enter New Title: ")
    date = input("Enter New Date (YYYY-MM-DD): ")
    cursor.execute("UPDATE Exams SET title=?, date=? WHERE exam_id=?", (title, date, exam_id))
    conn.commit()
    print("✅ Exam updated")

def delete_exam():
    view_exams()
    exam_id = int(input("Enter Exam ID to delete: "))
    cursor.execute("DELETE FROM Exams WHERE exam_id=?", (exam_id,))
    cursor.execute("DELETE FROM Questions WHERE exam_id=?", (exam_id,))
    cursor.execute("DELETE FROM Results WHERE exam_id=?", (exam_id,))
    conn.commit()
    print("✅ Exam deleted")

# -----------------------------
# QUESTION MANAGEMENT
# -----------------------------
def add_question():
    view_exams()
    exam_id = int(input("Enter Exam ID to add question: "))
    question_text = input("Enter Question Text: ")
    option1 = input("Option 1: ")
    option2 = input("Option 2: ")
    option3 = input("Option 3: ")
    option4 = input("Option 4: ")
    correct_option = int(input("Correct Option (1-4): "))
    marks = int(input("Marks for this question: "))
    cursor.execute('''INSERT INTO Questions (exam_id, question_text, option1, option2, option3, option4, correct_option, marks)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                   (exam_id, question_text, option1, option2, option3, option4, correct_option, marks))
    # Update total marks in exam
    cursor.execute("UPDATE Exams SET total_marks = total_marks + ? WHERE exam_id=?", (marks, exam_id))
    conn.commit()
    print("✅ Question added")

def view_questions():
    cursor.execute('''SELECT q.question_id, e.title, q.question_text, q.option1, q.option2, q.option3, q.option4, q.correct_option, q.marks
                      FROM Questions q
                      JOIN Exams e ON q.exam_id = e.exam_id''')
    for row in cursor.fetchall():
        print(row)

def update_question():
    view_questions()
    question_id = int(input("Enter Question ID to update: "))
    question_text = input("Enter New Question Text: ")
    option1 = input("Option 1: ")
    option2 = input("Option 2: ")
    option3 = input("Option 3: ")
    option4 = input("Option 4: ")
    correct_option = int(input("Correct Option (1-4): "))
    marks = int(input("Marks for this question: "))
    # Update question
    cursor.execute('''UPDATE Questions SET question_text=?, option1=?, option2=?, option3=?, option4=?, correct_option=?, marks=? WHERE question_id=?''',
                   (question_text, option1, option2, option3, option4, correct_option, marks, question_id))
    conn.commit()
    print("✅ Question updated")

def delete_question():
    view_questions()
    question_id = int(input("Enter Question ID to delete: "))
    # Deduct marks from exam
    cursor.execute("SELECT exam_id, marks FROM Questions WHERE question_id=?", (question_id,))
    exam_id, marks = cursor.fetchone()
    cursor.execute("UPDATE Exams SET total_marks = total_marks - ? WHERE exam_id=?", (marks, exam_id))
    cursor.execute("DELETE FROM Questions WHERE question_id=?", (question_id,))
    conn.commit()
    print("✅ Question deleted")

# -----------------------------
# EXAM TAKING & RESULTS
# -----------------------------
def assign_exam_to_student():
    view_exams()
    exam_id = int(input("Enter Exam ID: "))
    view_users()
    student_id = int(input("Enter Student ID: "))
    # Check if result already exists
    cursor.execute("SELECT * FROM Results WHERE exam_id=? AND student_id=?", (exam_id, student_id))
    if cursor.fetchone():
        print("❌ Exam already assigned or completed")
        return
    cursor.execute("INSERT INTO Results (exam_id, student_id, score, submitted_at) VALUES (?, ?, ?, ?)",
                   (exam_id, student_id, 0, None))
    conn.commit()
    print("✅ Exam assigned")

def take_exam():
    view_users()
    student_id = int(input("Enter your Student ID: "))
    # List assigned exams
    cursor.execute('''SELECT r.result_id, e.title
                      FROM Results r
                      JOIN Exams e ON r.exam_id = e.exam_id
                      WHERE r.student_id=? AND r.submitted_at IS NULL''', (student_id,))
    exams = cursor.fetchall()
    if not exams:
        print("❌ No exams to take")
        return
    print("Assigned Exams:")
    for ex in exams:
        print(ex)
    result_id = int(input("Enter Result ID for exam to take: "))
    # Get questions
    cursor.execute("SELECT exam_id FROM Results WHERE result_id=?", (result_id,))
    exam_id = cursor.fetchone()[0]
    cursor.execute("SELECT * FROM Questions WHERE exam_id=?", (exam_id,))
    questions = cursor.fetchall()
    score = 0
    for q in questions:
        print(f"\nQ{q[0]}: {q[2]}")
        print(f"1. {q[3]}  2. {q[4]}  3. {q[5]}  4. {q[6]}")
        ans = int(input("Your Answer (1-4): "))
        if ans == q[7]:
            score += q[8]
    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE Results SET score=?, submitted_at=? WHERE result_id=?", (score, submitted_at, result_id))
    conn.commit()
    print(f"✅ Exam submitted. Your score: {score}")

def view_results():
    cursor.execute('''SELECT r.result_id, u.name, e.title, r.score, e.total_marks, r.submitted_at
                      FROM Results r
                      JOIN Users u ON r.student_id = u.user_id
                      JOIN Exams e ON r.exam_id = e.exam_id''')
    for row in cursor.fetchall():
        print(row)

def rank_list():
    cursor.execute('''SELECT u.name, e.title, r.score
                      FROM Results r
                      JOIN Users u ON r.student_id = u.user_id
                      JOIN Exams e ON r.exam_id = e.exam_id
                      ORDER BY r.score DESC''')
    for row in cursor.fetchall():
        print(row)

# -----------------------------
# MAIN MENU
# -----------------------------
def menu():
    while True:
        print("\n--- Online Examination System ---")
        print("1. Manage Users")
        print("2. Manage Exams")
        print("3. Manage Questions")
        print("4. Assign Exams / Take Exams")
        print("5. View Results / Rank List")
        print("6. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            print("a. Add User\nb. View Users\nc. Update User\nd. Delete User")
            sub = input("Choice: ")
            if sub == "a": add_user()
            elif sub == "b": view_users()
            elif sub == "c": update_user()
            elif sub == "d": delete_user()

        elif choice == "2":
            print("a. Create Exam\nb. View Exams\nc. Update Exam\nd. Delete Exam")
            sub = input("Choice: ")
            if sub == "a": create_exam()
            elif sub == "b": view_exams()
            elif sub == "c": update_exam()
            elif sub == "d": delete_exam()

        elif choice == "3":
            print("a. Add Question\nb. View Questions\nc. Update Question\nd. Delete Question")
            sub = input("Choice: ")
            if sub == "a": add_question()
            elif sub == "b": view_questions()
            elif sub == "c": update_question()
            elif sub == "d": delete_question()

        elif choice == "4":
            print("a. Assign Exam to Student\nb. Take Exam")
            sub = input("Choice: ")
            if sub == "a": assign_exam_to_student()
            elif sub == "b": take_exam()

        elif choice == "5":
            print("a. View Results\nb. Rank List")
            sub = input("Choice: ")
            if sub == "a": view_results()
            elif sub == "b": rank_list()

        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("❌ Invalid Choice")

# -----------------------------
# RUN SYSTEM
# -----------------------------
if __name__ == "__main__":
    menu()
