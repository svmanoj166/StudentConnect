import datetime

def MenuHandle(menu_name,menu_options,menu_auth=None,user_role=None):
    print(f"Menu: {menu_name}")
    for idx, option in enumerate(menu_options, start=1):
        print(f"{idx}. {option}")
    try:
        choice = int(input("Select an option: "))
    except ValueError:
        choice = -1
    if 1 <= choice <= len(menu_options):
        if menu_auth is not None and len(menu_auth) != 0 and menu_auth[choice - 1] is not None:
            if user_role not in menu_auth[choice - 1]:
                print("Access Denied: You do not have the required privileges to access this option.")
                return None
        return menu_options[choice - 1]
    else:
        
        return None