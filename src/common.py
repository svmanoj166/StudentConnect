import datetime
import functools

class Person:
    def __init__(self, name, dob):
        self.name = name
        self.dob = dob
def log_decorator(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"Logging: {func.__doc__} with parameters {args}, {kwargs}")
        with open("updates_log.log", "a") as log_file:
            log_file.write(f"{datetime.datetime.now()}: {func.__doc__} with parameters {args}\n")               
        return result
    return wrapper