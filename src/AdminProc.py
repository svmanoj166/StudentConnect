import MenuProc
import UserProc
import ReportProc

def admin_menu(user):
    if user.role != 'admin':
        raise UserProc.insufficient_previlege('User does not have admin privileges', user.id, user.role)
        return
    admin_options = ["User Maintenance", "View Reports", "Back"]
    while True:
        choice = MenuProc.MenuHandle("Admin Menu", admin_options)
        if choice == "User Maintenance":
            UserProc.user_menu()
            # Call user maintenance function here
        elif choice == "View Reports":
            ReportProc.reports_menu(user)
            # Call view reports function here
        elif choice == "Back":
            print("Exiting Admin Menu.")
            break
        else:
            print("Invalid option. Please try again.")
    