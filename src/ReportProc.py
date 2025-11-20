import datetime
import sqlite3
import MenuProc
def course_toppers(course_id, db):
    """Generate a report of top performers in a course."""
    course_id = course_id.upper()
    cursor = db.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name, e.marks_obtained
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        WHERE e.course_id = ?
        ORDER BY e.marks_obtained DESC
        LIMIT 5
    ''', (course_id,))
    top_students = cursor.fetchall()
    print(f"Top Performers in Course {course_id}:")
    for student in top_students:
        print(f"Student ID: {student[0]}, Name: {student[1]}, Marks: {student[2]}")
def instructor_performance(instructor_id, db):
    """Generate a report of an instructor's course performance."""
    instructor_id = instructor_id.upper()
    cursor = db.cursor()
    cursor.execute('''
        SELECT c.course_id, c.course_name, AVG(e.marks_obtained) as avg_marks
        FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        WHERE c.instructor_id = ?
        GROUP BY c.course_id, c.course_name
    ''', (instructor_id,))
    courses = cursor.fetchall()
    print(f"Performance Report for Instructor {instructor_id}:")
    for course in courses:
        print(f"Course ID: {course[0]}, Course Name: {course[1]}, Average Marks: {course[2]:.2f}")
def student_progress(student_id, db):
    """Generate a report of a student's progress across all enrolled courses."""
    cursor = db.cursor()
    cursor.execute('''
        SELECT c.course_id, c.course_name, e.marks_obtained
        FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        WHERE e.student_id = ?
    ''', (student_id,))
    courses = cursor.fetchall()
    print(f"Progress Report for Student {student_id}:")
    for course in courses:
        print(f"Course ID: {course[0]}, Course Name: {course[1]}, Marks Obtained: {course[2]}")
def overall_performance(db):
    """Generate an overall performance report for all students."""
    cursor = db.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name, AVG(e.marks_obtained) as avg_marks
        FROM students s
        JOIN enrollments e ON s.student_id = e.student_id
        GROUP BY s.student_id, s.name
        ORDER BY avg_marks DESC
    ''')
    students = cursor.fetchall()
    print("Overall Student Performance Report:")
    for student in students:
        print(f"Student ID: {student[0]}, Name: {student[1]}, Average Marks: {student[2]:.2f}")
def all_courses_performance(db):
    """Generate a report of average performance across all courses."""
    cursor = db.cursor()
    cursor.execute('''
        SELECT c.course_id, c.course_name, AVG(e.marks_obtained) as avg_marks
        FROM courses c
        JOIN enrollments e ON c.course_id = e.course_id
        GROUP BY c.course_id, c.course_name
        ORDER BY avg_marks DESC
    ''')
    courses = cursor.fetchall()
    print("Overall Course Performance Report:")
    for course in courses:
        print(f"Course ID: {course[0]}, Course Name: {course[1]}, Average Marks: {course[2]:.2f}")

db_path = 'SmartEduDB.db'
def reports_menu(user):
    if user.role not in ('admin', 'instructor'):
        print("Access Denied: You do not have the required privileges to access reports.")
        return
    db = sqlite3.connect(db_path)
    report_options = [
        "Course Toppers",
        "Instructor Performance",
        "Student Progress",
        "Overall Students Performance",
        "Overall Course Performance",
        "Exit"
    ]
    while True:
        choice = MenuProc.MenuHandle("Reports Menu", report_options)
        if choice == "Course Toppers":
            course_id = input("Enter Course ID: ")
            course_toppers(course_id, db)
        elif choice == "Instructor Performance":
            instructor_id = input("Enter Instructor ID: ")
            instructor_performance(instructor_id, db)
        elif choice == "Student Progress":
            student_id = input("Enter Student ID: ")
            student_progress(student_id, db)
        elif choice == "Overall Students Performance":
            overall_performance(db)
        elif choice == "Overall Course Performance":
            all_courses_performance(db)
        elif choice == "Exit":
            print("Exiting Reports Menu.")
            break
        else:
            print("Invalid choice, please try again.")
    db.close()