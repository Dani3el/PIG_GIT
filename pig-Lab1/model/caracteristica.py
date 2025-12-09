class Departament:
    ALLOWED_DEPARTMENTS = ("Human Resources", "Finance", "Engineering", "Marketing", "Unknown")

    @staticmethod
    def _normalize_department(value: str) -> str:
        s = (value or "").strip()
        if not s:
            return "Unknown"
        k = s.casefold()
        alias = {
            "hr": "Human Resources",
            "human resources": "Human Resources",
            "fin": "Finance",
            "finance": "Finance",
            "eng": "Engineering",
            "engineering": "Engineering",
            "it": "Engineering",
            "mkt": "Marketing",
            "marketing": "Marketing",
        }
        v = alias.get(k, s.title())
        return v if v in Departament.ALLOWED_DEPARTMENTS else "Unknown"

    def __init__(self, department: str):
        self.department = self._normalize_department(department)


class Subject:
    ALLOWED_SUBJECTS = ("Mathematics", "Physics", "Chemistry", "Biology", "Unknown")

    @staticmethod
    def _normalize_subject(value: str) -> str:
        s = (value or "").strip()
        if not s:
            return "Unknown"
        k = s.casefold()
        alias = {
            "math": "Mathematics", "mathematics": "Mathematics",
            "phys": "Physics", "physics": "Physics",
            "chem": "Chemistry", "chemistry": "Chemistry",
            "bio": "Biology", "biology": "Biology",
        }
        v = alias.get(k, s.title())
        return v if v in Subject.ALLOWED_SUBJECTS else "Unknown"

    def __init__(self, subject: str):
        self.subject = self._normalize_subject(subject)


class Speciality:
    ALLOWED_SPECIALTIES = ("Computer Science", "Mathematics", "Physics", "Engineering", "Unknown")

    @staticmethod
    def _normalize_speciality(value: str) -> str:
        s = (value or "").strip()
        if not s:
            return "Unknown"
        k = s.casefold()
        alias = {
            "cs": "Computer Science", "computer science": "Computer Science",
            "math": "Mathematics", "mathematics": "Mathematatics",
            "phys": "Physics", "physics": "Physics",
            "eng": "Engineering", "engineering": "Engineering", "it": "Engineering",
        }
        v = alias.get(k, s.title())
        return v if v in Speciality.ALLOWED_SPECIALTIES else "Unknown"

    def __init__(self, speciality: str):
        self.speciality = self._normalize_speciality(speciality)


class Employee(Departament):
    def __init__(self, name, id, salary, department):
        self.name = name
        self.id = id
        self.salary = salary
        Departament.__init__(self, department)
