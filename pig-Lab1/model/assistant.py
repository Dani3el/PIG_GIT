from model.caracteristica import Employee

class Assistant(Employee):  # Assistant inherits from Employee
    def __init__(self, name, id, salary, department):
        super().__init__(name, id, salary, department)