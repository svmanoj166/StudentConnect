from datetime import datetime
import os
import MenuProc
import UserProc
import AdminProc
import CourseProc
import StudProc
import InstructorProc
import sys
def main_menu(user):
    menu_name = "Main Menu"
    menu_options = ["Course Management", "Student Management",
                    "Instructor Management", "Administration", "Exit"]
    menu_auth = [('admin', 'instructor'),None,('admin','instructor'),('admin',),None]
    while True:
            choice = MenuProc.MenuHandle(menu_name, menu_options, menu_auth, user.role)
        #try:
            if choice == "Course Management":
                CourseProc.course_menu(user)
                # Call course management function here
            elif choice == "Student Management":
                StudProc.stud_menu(user)
                # Call student management function here
            elif choice == "Instructor Management":
                InstructorProc.instr_menu(user)
                # Call instructor management function here
            elif choice == "Administration":
                AdminProc.admin_menu(user)
                # Call administration function here
            elif choice == "Exit":
                print("Exiting the application.")
                break
            else:
                print("Invalid choic, please try again.")
            
        #except Exception as e:
          #  print(e.message)  
        
        
    return choice 
print(sys.path[0])
userobj=UserProc.get_credentials()
if userobj:
    main_menu(userobj)
