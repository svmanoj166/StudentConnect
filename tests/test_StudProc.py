from MSmartEdu.src import StudProc
def test_add_student():
    # Test adding a student
    studobj=StudProc.student(200)
    studobj.add_stud("Ajay","test@gmail.com")
    studobj.get_stud_info()
    assert studobj.name == "Ajay"
    assert studobj.email == "test@gmail.com"
    # Add assertions here to verify the student was added correctly