import sqlite3
import MenuProc
import getpass
import common
import datetime

class authentication_failed(Exception):
    def __init__(self, message,id,password):
        self.id = id
        self.password = password
        self.message = message
        super().__init__(self.message)

class insufficient_previlege(Exception):
    def __init__(self, message,id,role):
        self.id = id
        self.role = role
        self.message = message
        super().__init__(self.message)

class user_not_found(Exception):
    def __init__(self, message,id):
        self.id = id
        self.message = message
        super().__init__(self.message)

class user(common.Person):
    def __init__(self, id):
        self.id = id
        self.db=sqlite3.connect('SmartEduDB.db')
        self.cursor=self.db.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users ( id TEXT PRIMARY KEY,
        name TEXT NOT NULL,password TEXT NOT NULL,role TEXT DEFAULT 'student') ''')
    
    def updates_decorator(func):  
        def wrapper(self, *args, **kwargs):
            try:
                print(f"Attempting to execute {func.__name__} with args: {args}, kwargs: {kwargs}" )
                if func.__name__ != "delete_user":           
                    common.Person.__init__(self, args[1], None)  # Initialize name from args
                if "update" in func.__name__ or "delete" in func.__name__:
                    try:
                        self.get_user_info()
                    except user_not_found as e:
                        print(e.message,e.id)   
                        return None
                if func.__name__ == "enroll" or "add" in func.__name__:
                    try:
                        self.get_user_info()
                    except user_not_found:
                        pass
                    else:
                        print(f"User with ID {self.id} already exists.")
                        return None
                    
                result = func(self, *args, **kwargs)
            except Exception as e:
                print(f"An error occurred: {e}")
            else:
                self.db.commit()
                with open("updates_log.log", "a") as log_file:
                    log_file.write(f"{datetime.datetime.now()}: {func.__doc__} with id {self.id}\n")
                try:
                    if func.__name__ != "delete_user":
                        self.get_user_info()
                except user_not_found as e:
                    print(e.message,e.id)   
            return None
        return wrapper
    @updates_decorator
    def enroll(self, name,password,role="student"):
        ''' Enroll a new user '''
        self.cursor.execute("INSERT INTO users (id, name,password,role) "+
                            "VALUES (?,?,?,?)", (self.id, name,password,role))
        print(f"User {name} enrolled with ID {self.id}")    
    @updates_decorator
    def update_user(self, name,password,role="student"):
        ''' Update user details '''
        self.cursor.execute("UPDATE users SET name=?, password=?, role=? WHERE id=?",
                            (name,password,role,self.id))
        print(f"User {self.id} updated to Name: {name}, Role: {role}")
    @updates_decorator
    def delete_user(self):
        ''' Delete a user '''
        self.cursor.execute("DELETE FROM users WHERE id=?", (self.id,))
        print(f"User {self.id} deleted.")

    def authenticate(self, id,password):
        self.cursor.execute("SELECT * FROM users WHERE id=? AND password=?", (id,password))
        result = self.cursor.fetchone()
        if result:
            print(f"User {id} authenticated successfully.")
            self.role=result[3]
            return True
        else:
            raise authentication_failed('User not authenticated',id,password)
            print(f"Authentication failed for user {id}.")
            return False
    def get_user_info(self):
        self.cursor.execute("SELECT * FROM users WHERE id=?", (self.id,))
        result = self.cursor.fetchone()
        if result:
            return {"id": result[0], "name": result[1],"role": result[3]}
        else:
            raise user_not_found('User not found',self.id)
            

def user_menu():
    user_options = ["Enroll","Update User","Delete User", "Get User Info","List Users", "Exit"]
    while True:
         choice = MenuProc.MenuHandle("User Menu", user_options)
         if choice == "Enroll":
              id = input("Enter ID: ").capitalize
              name = input("Enter Name: ")
              password = input("Enter Password: ")
              role = input("Enter Role (student/instructor/admin): ")
              new_user = user(id)
              new_user.enroll(name, password,role)
         elif choice == "Update User":
              id = input("Enter ID: ").capitalize
              name = input("Enter New Name: ")
              password = input("Enter New Password: ")
              role = input("Enter New Role (student/instructor/admin): ")
              updateuser=user(id)
              updateuser.update_user(name, password,role)  
         elif choice == "Delete User":
              id = input("Enter ID: ").capitalize
              deluser=user(id)
              deluser.delete_user()   
         elif choice == "List Users":
                db=sqlite3.connect('SmartEduDB.db')
                cursor=db.cursor()
                try:
                    cursor.execute("SELECT * FROM users")
                except sqlite3.OperationalError as e:
                    print("No users found.")
                else:    
                    users = cursor.fetchall()
                    for usr in users:
                        print(f"ID: {usr[0]}, Name: {usr[1]}, Password:{usr[2]}, Role: {usr[3]}")
                db.close()
                
         elif choice == "Get User Info":
              id = input("Enter ID: ")
              getuser=user(id)
              info = getuser.get_user_info()
              print(info if info else "User not found.")
         elif choice == "Exit":
              print("Exiting User Menu.")
              break
         else:
              print("Invalid option. Please try again.")

def get_credentials():
    id = input("Enter User ID: ")
    password = getpass.getpass("Enter Password: ")
    userobj=user(id)
    try:
        if userobj.authenticate(id,password):
            print("Access Granted")
            return userobj
    except authentication_failed as e:
        print(e.message)
    
    