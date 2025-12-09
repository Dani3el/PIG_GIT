from model.person import Person
from model.caracteristica import Speciality

class Student(Person, Speciality):  # Student inherits from Person
    def __init__(self, name, id, grade, speciality):
        Person.__init__(self, name, id)
        Speciality.__init__(self, speciality)
        self.grade = grade