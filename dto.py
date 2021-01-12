# Data Transfer Objects:
class Student:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Assignment:
    def __init__(self, num, expected_output):
        self.num = num
        self.expected_output = expected_output


class Grade:
    def __init__(self, student_id, assignment_num, grade):
        self.student_id = student_id
        self.assignment_num = assignment_num
        self.grade = grade