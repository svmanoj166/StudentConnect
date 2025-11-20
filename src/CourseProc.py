import MenuProc
import UserProc
import sqlite3
import datetime

class course_not_found(Exception):
    def __init__(self, message,course_id):
        self.course_id = course_id.upper()
        self.message = message
        super().__init__(self.message)
class course:
    def __init__(self, course_id):
        self.course_id = course_id.upper()
        self.db=sqlite3.connect('SmartEduDB.db')
        self.cursor=self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses ( course_id TEXT PRIMARY KEY,
        course_name TEXT NOT NULL, instructor_id TEXT, total_marks INTEGER NOT NULL) ''')
    
    def updates_decorator(func):  
        def wrapper(self, *args, **kwargs):
            try:
                self.course_id=self.course_id.upper()
                if "update" in func.__name__ or "delete" in func.__name__:
                    try:
                        self.get_course_info()
                    except course_not_found as e:
                        print(e.message,e.course_id)   
                        return None
                if func.__name__ == "enroll" or "add" in func.__name__:
                    try:
                        self.get_course_info()
                    except course_not_found:
                        pass
                    else:
                        print(f"User with ID {self.course_id} already exists.")
                        return None
                    
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.now()}: {func.__doc__} with id {self.course_id}\n")
                try:
                    if func.__name__ != "delete_course":
                        self.get_course_info()
                except course_not_found as e:
                    print(e.message,e.course_id)   
            return None
        return wrapper
    @updates_decorator
    def add_course(self, course_name, instructor_id, total_marks):
        ''' Add a new course '''
        self.cursor.execute("INSERT INTO courses (course_id, course_name, instructor_id, total_marks) VALUES (?, ?, ?, ?)",
                            (self.course_id, course_name, instructor_id, total_marks))
        
        print(f"Course {course_name} added successfully.")
    @updates_decorator
    def update_course(self, course_name=None, instructor_id=None, total_marks=None):
        ''' Update course details '''
        if course_name:
            self.cursor.execute("UPDATE courses SET course_name = ? WHERE course_id = ?", (course_name, self.course_id))
        if instructor_id:
            self.cursor.execute("UPDATE courses SET instructor_id = ? WHERE course_id = ?", (instructor_id, self.course_id))
        if total_marks is not None:
            self.cursor.execute("UPDATE courses SET total_marks = ? WHERE course_id = ?", (total_marks, self.course_id))
        
        print(f"Course {self.course_id} updated successfully.")
    @updates_decorator
    def delete_course(self):
        ''' Delete a course '''
        self.cursor.execute("DELETE FROM courses WHERE course_id = ?", (self.course_id,))
        self.cursor.execute("DELETE FROM enrollments WHERE course_id = ?", (self.course_id,))   
        print(f"Course {self.course_id} deleted successfully.")
    def get_course_info(self):
        self.cursor.execute("SELECT * FROM courses WHERE course_id = ?", (self.course_id,))
        course = self.cursor.fetchone()
        if not course:
            raise course_not_found(f"Course with ID {self.course_id} not found.", self.course_id)
        else:
            #print(f"Course ID: {course[0]}, Name: {course[1]}, Instructor ID: {course[2]}, Total Marks: {course[3]}")
            self.course_name = course[1]
            self.instructor_id = course[2]
            self.total_marks = course[3]
       
def course_menu(user):
    if user.role != 'admin' and user.role != 'instructor':
        raise UserProc.insufficient_previlege('User does not have course management privileges', user.id, user.role)
        return      
    course_options=["View Courses", "Add Course", "Update Course","Remove Course", "Back"]
    while True:
        choice = MenuProc.MenuHandle("Course Menu", course_options)
        if choice == "View Courses":
            # Call view courses function here
            db=sqlite3.connect('SmartEduDB.db')
            cursor=db.cursor()
            try:
                cursor.execute("SELECT * FROM courses")
            except sqlite3.OperationalError as e:
                print("No courses found.")
            else:
                courses = cursor.fetchall()
                if not courses:
                    print("No courses available.")
                else:
                    for cours in courses:
                        print(f"Course ID: {cours[0]}, Name: {cours[1]}, Instructor ID: {cours[2]}, Total Marks: {cours[3]}")
            db.close()
               
        elif choice == "Add Course":
            # Call add course function here
            course_id = input("Enter Course ID: ")
            course_name = input("Enter Course Name: ")
            instructor_id = input("Enter Instructor ID: ")
            total_marks = int(input("Enter Total Marks: "))
            new_course = course(course_id)
            new_course.add_course(course_name, instructor_id, total_marks)
        elif choice == "Update Course":
            # Call update course function here
            course_id = input("Enter Course ID to update: ")
            course_name = input("Enter New Course Name (leave blank to keep unchanged): ")
            instructor_id = input("Enter New Instructor ID (leave blank to keep unchanged): ")
            total_marks_input = input("Enter New Total Marks (leave blank to keep unchanged): ")
            total_marks = int(total_marks_input) if total_marks_input else None
            update_course = course(course_id)
            update_course.update_course(course_name if course_name else None,
                                        instructor_id if instructor_id else None,
                                        total_marks)
        elif choice == "Remove Course":
            # Call remove course function here
            course_id = input("Enter Course ID to remove: ")
            del_course = course(course_id)
            del_course.delete_course()
        elif choice == "Back":
            print("Returning to previous menu.")
            break
        else:
            print("Invalid choice. Please try again.")