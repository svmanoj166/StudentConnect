import sqlite3
from datetime import datetime
import MenuProc
import common
import CourseProc
import functools

class student_not_found(Exception):
    def __init__(self, message,student_id):
        self.student_id = student_id
        self.message = message
        super().__init__(self.message)
class student(common.Person):
    def __init__(self, student_id):
        self.student_id = student_id
        self.db = sqlite3.connect('SmartEduDB.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    
    def updates_decorator(func):  
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                if "update" in func.__name__ or "delete" in func.__name__:
                    try:
                        self.get_stud_info()
                    except student_not_found as e:
                        print(e.message,e.student_id)   
                        return None
                if func.__name__ == "enroll" or "add" in func.__name__:
                    try:
                        self.get_stud_info()
                    except student_not_found:
                        pass
                    else:
                        print(f"Student with ID {self.student_id} already exists.")
                        return None
                    
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.now()}: {func.__doc__} with id {self.student_id}\n")
                try:
                    if func.__name__ != "delete_stud":
                        self.get_stud_info()
                except student_not_found as e:
                    print(e.message,e.student_id)   
            return None
        return wrapper    
    
    @updates_decorator
    def add_stud(self, name, email):
        ''' Add a new student '''
        self.cursor.execute("INSERT INTO students (student_id, name, email) VALUES (?, ?, ?)",
                            (self.student_id, name, email))
        print(f"Student {name} added successfully.")
    
    @updates_decorator
    def update_stud(self, name=None, email=None):
        ''' Update student details '''
        if name:
            self.cursor.execute("UPDATE students SET name = ? WHERE student_id = ?", (name, self.student_id))
        if email:
            self.cursor.execute("UPDATE students SET email = ? WHERE student_id = ?", (email, self.student_id))
        print(f"Student ID {self.student_id} updated successfully.")
    
    @updates_decorator
    def delete_stud(self):
        ''' Delete a student '''
        self.cursor.execute("DELETE FROM students WHERE student_id = ?", (self.student_id,))
        self.cursor.execute("DELETE FROM enrollments WHERE student_id = ?", (self.student_id,))
        print(f"Student ID {self.student_id} deleted successfully.")

    
    def get_stud_info(self):
        self.cursor.execute("SELECT * FROM students WHERE student_id = ?", (self.student_id,))
        student = self.cursor.fetchone()
        if not student:
            raise student_not_found("Student not found with ID", self.student_id)
        else:
            self.name = student[1]
            self.email = student[2]
    def view_enrolled_courses(self):
        try:
            self.cursor.execute('''SELECT c.course_id, c.course_name, e.enrollment_date, e.marks_obtained
                                FROM courses c
                                JOIN enrollments e ON c.course_id = e.course_id
                                WHERE e.student_id = ?''', (self.student_id,))
        except sqlite3.OperationalError as e:
            print("Error fetching enrolled courses:", e)
            return
        courses = self.cursor.fetchall()
        if not courses:
            print("No enrolled courses found.")
        else:
            for course in courses:
                print(f"Course ID: {course[0]}, Course Name: {course[1]}, Enrollment Date: {datetime.strptime(course[2],'%Y-%m-%d').strftime("%d-%b-%Y")}, Marks Obtained: {course[3]}")
    
class enrollment_not_found(Exception):
    def __init__(self, message,student_id,course_id):
        self.student_id = student_id
        self.course_id = course_id.upper()
        self.message = message
        super().__init__(self.message)
class enrollment(student, CourseProc.course):
    def __init__(self, student_id, course_id):
        student.__init__(self, student_id)
        CourseProc.course.__init__(self, course_id)
        self.db = sqlite3.connect('SmartEduDB.db')
        self.cursor = self.db.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS students (student_id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS enrollments (
                            student_id INTEGER,
                            course_id TEXT, enrollment_date TEXT,marks_obtained INTEGER DEFAULT 0,
                            PRIMARY KEY (student_id, course_id),
                            FOREIGN KEY (student_id) REFERENCES students(student_id),
                            FOREIGN KEY (course_id) REFERENCES courses(course_id)
                            )''')
    def updates_decorator_enrollments(func):  
        def wrapper(self, *args, **kwargs):
            try:
                if "unenroll" in func.__name__ or "enroll" in func.__name__:
                    try:
                        self.get_stud_info()
                    except student_not_found as e:
                        print(e.message,e.student_id)   
                        return None
                    try:
                        self.get_course_info()
                    except CourseProc.course_not_found as e:
                        print(e.message,e.course_id)   
                        return None
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.now()}: {func.__doc__} with Student ID {self.student_id} and Course ID {self.course_id}\n")
                try:
                    if func.__name__ != "unenroll":
                        self.get_enrollment_info()
                except enrollment_not_found as e:
                    print(e.message,e.student_id,e.course_id)   
            return None
        return wrapper
    def get_enrollment_info(self):
        self.cursor.execute("SELECT * FROM enrollments WHERE student_id = ? AND course_id = ?", (self.student_id, self.course_id))
        enrollment = self.cursor.fetchone()
        if not enrollment:
            raise enrollment_not_found("Enrollment not found for Student ID and Course ID", (self.student_id, self.course_id))
        else:
            self.enrollment_date = enrollment[2]
            self.marks_obtained = enrollment[3]
    @updates_decorator_enrollments
    def enroll(self):
        ''' Student Enrollment in Courses '''
        try:
            self.cursor.execute("INSERT INTO enrollments (student_id, course_id,enrollment_date) VALUES (?, ?,?)", (self.student_id, self.course_id, str(datetime.now().date())))
        except sqlite3.IntegrityError:
            print(f"Already enrolled in course ID {self.course_id}.")
        else:
            print(f"Enrolled in course ID {self.course_id} successfully.")
    @updates_decorator_enrollments
    def unenroll(self):
        ''' Student Unenrollment from Courses '''
        try:
            self.cursor.execute("DELETE FROM enrollments WHERE student_id = ? AND course_id = ?", (self.student_id, self.course_id))
        except sqlite3.IntegrityError:
            print(f"Not enrolled in course ID {self.course_id}.")
        else:
            print(f"Unenrolled from course ID {self.course_id} successfully.")
def stud_menu(user):
    student_options = ["Add Student","Update Student","Delete Student","List Students","View Enrolled Courses", "Enroll in Course", "Unenroll from Course", "Back"]
    while True:
        choice = MenuProc.MenuHandle("Student Menu", student_options)
        if choice == "Add Student":
            # Call add student function here
            student_id=int(input("Enter Student ID: "))
            name = input("Enter Student Name: ")
            email = input("Enter Student Email: ")
            stud=student(student_id)
            stud.add_stud(name, email)
        elif choice == "Update Student":
            # Call update student function here
            student_id=int(input("Enter Student ID to update: "))
            name = input("Enter New Name (leave blank to keep current): ")
            email = input("Enter New Email (leave blank to keep current): ")
            stud=student(student_id)
            stud.update_stud(name if name else None, email if email else None)

        elif choice == "Delete Student":
            # Call delete student function here
            student_id=int(input("Enter Student ID to delete: "))
            stud=student(student_id)
            stud.delete_stud()
        elif choice == "List Students":
            # Call list students function here
            
            db=sqlite3.connect('SmartEduDB.db')
            cursor=db.cursor()
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            if not students:
                print("No students found.")
            else:
                for stud in students:
                    print(f"Student ID: {stud[0]}, Name: {stud[1]}, Email: {stud[2]}")
        elif choice == "View Enrolled Courses":
            # Call view enrolled courses function here
            student_id=int(input("Enter Student ID to view enrolled courses: "))
            stud=student(student_id)
            stud.view_enrolled_courses()
        elif choice == "Enroll in Course":
            # Call enroll in course function here
            student_id=int(input("Enter Student ID to enroll in a course: "))
            course_id = input("Enter Course ID to enroll: ")
            enroll= enrollment(student_id, course_id)
            enroll.enroll()
        elif choice == "Unenroll from Course":
            # Call unenroll from course function here
            student_id=int(input("Enter Student ID to unenroll from a course: "))
            course_id = input("Enter Course ID to unenroll: ")
            enroll= enrollment(student_id, course_id)
            enroll.unenroll()
        elif choice == "Back":
            print("Returning to previous menu.")
            break
        else:
            print("Invalid option. Please try again.")