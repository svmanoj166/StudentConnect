import UserProc
import MenuProc
import sqlite3
import common
import CourseProc
import StudProc
import datetime
class instructor_not_found(Exception):
    def __init__(self, message,instructor_id):
        self.instructor_id = instructor_id.upper()
        self.message = message
        super().__init__(self.message)
class instructor(common.Person):
    def __init__(self, instructor_id):
        self.instructor_id = instructor_id.upper()
        self.db=sqlite3.connect('SmartEduDB.db')
        self.cursor=self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS instructors ( instructor_id TEXT PRIMARY KEY,
        name TEXT NOT NULL, email TEXT UNIQUE NOT NULL) ''')
    def get_instructor_info(self):
        self.cursor.execute("SELECT * FROM instructors WHERE instructor_id = ?", (self.instructor_id,))
        instructor = self.cursor.fetchone()
        if not instructor:
            raise instructor_not_found("Instructor with ID not found:", self.instructor_id)
        self.name = instructor[1]
        self.email = instructor[2]
        return instructor
    def list_instructors(self):
        self.cursor.execute("SELECT instructor_id, name, email FROM instructors")
        instructors = self.cursor.fetchall()
        if not instructors:
            print("No instructors found.")
        else:
            for instr in instructors:
                print(f"instructor_id: {instr[0]}, Name: {instr[1]}, Email: {instr[2]}")
        
    def updates_decorator(func):  
        def wrapper(self, *args, **kwargs):
            try:
                self.instructor_id=self.instructor_id.upper()
                if "update" in func.__name__ or "delete" in func.__name__:
                    try:
                        self.get_instructor_info()
                    except instructor_not_found as e:
                        print(e.message,e.instructor_id)   
                        return None
                if func.__name__ == "add" or "register" in func.__name__:
                    try:
                        self.get_instructor_info()
                    except instructor_not_found:
                        pass
                    else:
                        print(f"Instructor with ID {self.instructor_id} already exists.")
                        return None
                    
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.now()}: {func.__doc__} with id {self.instructor_id}\n")
                try:
                    if func.__name__ != "delete_instructor":
                        self.get_instructor_info()
                except instructor_not_found as e:
                    print(e.message,e.instructor_id)   
            return None
        return wrapper
    @updates_decorator
    def add_instructor(self, name, email):
        ''' Add a new instructor '''
        self.cursor.execute("INSERT INTO instructors (instructor_id, name, email) VALUES (?, ?, ?)",
                            (self.instructor_id, name, email))
        
        print(f"Instructor {name} added successfully.")
    @updates_decorator
    def update_instructor(self, name=None, email=None):
        ''' Update instructor details '''
        if name:
            self.cursor.execute("UPDATE instructors SET name = ? WHERE instructor_id = ?", (name, self.instructor_id))
        if email:
            self.cursor.execute("UPDATE instructors SET email = ? WHERE instructor_id = ?", (email, self.instructor_id))
        
        print(f"Instructor {self.instructor_id} updated successfully.")
    @updates_decorator
    def delete_instructor(self):
        ''' Delete an instructor '''
        self.cursor.execute("DELETE FROM instructors WHERE instructor_id = ?", (self.instructor_id,))
        self.cursor.execute("UPDATE courses SET instructor_id = NULL WHERE instructor_id = ?", (self.instructor_id,))
        print(f"Instructor {self.instructor_id} deleted successfully.")
class InstructorNotAssingedToCourse(Exception):
    def __init__(self, message,instructor_id,course_id=None):
        self.instructor_id = instructor_id.upper()
        self.course_id = course_id.upper()
        self.message = message
        super().__init__(self.message)
class course_instructor(instructor,CourseProc.course):
    def __init__(self, instr_id, course_id):
        instructor.__init__(self, instr_id)
        CourseProc.course.__init__(self, course_id)
        
    def updates_decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.instructor_id=self.instructor_id.upper()
                self.course_id=self.course_id.upper()
                try:
                    self.get_instructor_info()
                except instructor_not_found as e:
                    print(e.message,e.instructor_id)   
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
                    log_file.write(f"{datetime.now()}: {func.__doc__} with id {self.instructor_id} and course id {self.course_id}\n")
                
            return None
        return wrapper
    def get_course_instructor_info(self):
        self.cursor.execute("SELECT * FROM courses WHERE course_id = ? AND instructor_id = ?", (self.course_id,self.instructor_id))
        course = self.cursor.fetchone()
        if not course:
            raise InstructorNotAssingedToCourse(f"Instructor with ID {self.instructor_id} is not assigned to course {self.course_id}.", self.instructor_id)
        else:
            print(f"Course ID: {course[0]}, Name: {course[1]}, Instructor ID: {course[2]}, Total Marks: {course[3]}")
            self.course_name = course[1]
            return course
    @updates_decorator
    def assign_course(self):
        ''' Assign an instructor to a course '''
        self.cursor.execute("UPDATE courses SET instructor_id = ? WHERE course_id = ?", (self.instructor_id, self.course_id))
        print(f"Instructor {self.instructor_id} assigned to course {self.course_id} successfully.")
class Stud_Course_Marks(StudProc.enrollment,course_instructor):
    def __init__(self, stud_id, course_id, instr_id):
        #StudProc.student.__init__(self, stud_id)
        #CourseProc.course.__init__(self, course_id)
        #instructor.__init__(self, instr_id)
        StudProc.enrollment.__init__(self, stud_id, course_id)
        course_instructor.__init__(self, instr_id, course_id)
    def updates_decorator(func):
        def wrapper(self, *args, **kwargs):
            try:
                self.student_id=self.student_id.upper()
                self.course_id=self.course_id.upper()
                self.instructor_id=self.instructor_id.upper()
                try:
                    self.get_instructor_info()
                except instructor_not_found as e:
                    print(e.message,e.instructor_id)   
                    return None
                try:
                    self.get_course_info()
                except CourseProc.course_not_found as e:
                    print(e.message,e.course_id)   
                    return None
                try:
                    self.get_stud_info()
                except StudProc.student_not_found as e:
                    print(e.message,e.student_id)   
                    return None
                try: self.get_enrollment_info()
                except StudProc.enrollment_not_found as e:
                    print(e.message,e.student_id,e.course_id)   
                    return None
                try: self.get_course_instructor_info()
                except InstructorNotAssingedToCourse as e:
                    print(e.message,e.instructor_id,e.course_id)   
                    return None
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.now()}: {func.__doc__} with Student ID {self.student_id}, Course ID {self.course_id}, Instructor ID {self.instructor_id}\n")
                
            return None
        return wrapper
    @updates_decorator
    def record_marks(self, marks_obtained):
        ''' Record marks for a student in a course '''
        if marks_obtained < 0 or marks_obtained > self.total_marks:
            print(f"Invalid marks. Please enter a value between 0 and {self.total_marks}.")
            return
        self.cursor.execute('''UPDATE enrollments 
                               SET marks_obtained = ? 
                               WHERE student_id = ? AND course_id = ?''', 
                               (marks_obtained, self.student_id, self.course_id))
        print(f"Marks {marks_obtained} recorded for student {self.student_id} in course {self.course_id} successfully.")
def instr_menu(user):
    menu_name = "Instructor Management Menu"
    menu_options = ["Add Instructor", "Update Instructor", "Delete Instructor",
                    "View Instructor Info", "List All Instructors","Assign Course", "Record Marks","Back to Main Menu"]
    
    while True:
        choice = MenuProc.MenuHandle(menu_name, menu_options)
        try:
            if choice == "Add Instructor":
                id = input("Enter Instructor ID: ").strip()
                name = input("Enter Instructor Name: ").strip()
                email = input("Enter Instructor Email: ").strip()
                instr = instructor(id)
                instr.add_instructor(name, email)
            elif choice == "Update Instructor":
                id = input("Enter Instructor ID to update: ").strip()
                instr = instructor(id)
                name = input("Enter new name (leave blank to keep current): ").strip()
                email = input("Enter new email (leave blank to keep current): ").strip()
                instr.update_instructor(name if name else None, email if email else None)
            elif choice == "Delete Instructor":
                id = input("Enter Instructor ID to delete: ").strip()
                instr = instructor(id)
                instr.delete_instructor()
            elif choice == "View Instructor Info":
                id = input("Enter Instructor ID to view: ").strip()
                instr = instructor(id)
                try:
                    instr_info = instr.get_instructor_info()
                    print(f"Instructor ID: {instr_info[0]}, Name: {instr_info[1]}, Email: {instr_info[2]}")
                except instructor_not_found as e:
                    print(e.message,e.id)   
            elif choice == "List All Instructors":
                instr = instructor("DUMMY")  # Dummy ID since we won't use it
                instr.list_instructors()
            elif choice == "Assign Course":
                instr_id = input("Enter Instructor ID: ").strip()
                course_id = input("Enter Course ID to assign: ").strip()
                ci = course_instructor(instr_id, course_id)
                ci.assign_course()
            elif choice == "Record Marks":
                stud_id = input("Enter Student ID: ").strip()
                course_id = input("Enter Course ID: ").strip()
                instr_id = input("Enter Your Instructor ID: ").strip()
                marks_obtained = float(input("Enter Marks Obtained: ").strip())
                scm = Stud_Course_Marks(stud_id, course_id, instr_id)
                scm.record_marks(marks_obtained)
            elif choice == "Back to Main Menu":
                break
            else:
                print("Invalid choice, please try again.")
        except Exception as e:
            print(e)  
        
    return choice