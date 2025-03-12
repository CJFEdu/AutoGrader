from typing import List, Dict

class Test:
    def __init__(self, name: str, passed: bool, output: str):
        self.name = name
        self.passed = passed
        self.output = output
    
    def to_dict(self):
        """Convert Test object to a dictionary for JSON serialization"""
        return {
            "name": self.name,
            "passed": self.passed,
            "output": self.output
        }

class Student:

    def __init__(self, first_name: str, last_name: str, username: str):
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.file_type = ""
        self.tests: List[Test] = []
        self.full_output = ""
        self.full_output_passed = False

    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        """Convert Student object to a dictionary for JSON serialization"""
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "file_type": self.file_type,
            "tests": [test.to_dict() for test in self.tests],
            "full_output": self.full_output,
            "full_output_passed": self.full_output_passed
        }

class Results:
    def __init__(self, tests: List[str]):
        self.tests = tests
        self.students: Dict[str, Student] = {}

    def add_student(self, student: Student):
        self.students[student.username] = student
        
    def to_dict(self):
        """Convert Results object to a dictionary for JSON serialization"""
        return {
            "tests": self.tests,
            "students": {username: student.to_dict() for username, student in self.students.items()}
        }

