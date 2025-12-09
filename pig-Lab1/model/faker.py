# model/faker.py
import random
import itertools
from typing import Dict, List
from model.teacher import Teacher
from model.student import Student
from model.assistant import Assistant
from model.caracteristica import Subject, Speciality  # folosește listele permise

_FIRST = [
    "Alex", "Mara", "Elena", "Daria", "Tudor", "Vlad", "Mihai", "Irina",
    "Andrei", "Sergiu", "Ioana", "Radu", "Bianca", "Cristina", "Matei",
]
_LAST = [
    "Ionescu", "Popescu", "Georgescu", "Marin", "Dumitrescu", "Enache",
    "Stoica", "Lungu", "Sandu", "Rusu", "Miron", "Vasilescu", "Petrescu",
]

_DEPARTMENTS = ["Human Resources", "Finance", "Engineering", "Marketing"]

_SUBJECTS = list(getattr(Subject, "ALLOWED_SUBJECTS", ("Mathematics", "Physics", "Chemistry", "Biology")))
_SPECIALITIES = list(getattr(Speciality, "ALLOWED_SPECIALTIES", ("Computer Science", "Mathematics", "Physics", "Engineering")))

_id_counter = itertools.count(10001)

def _name(rand: random.Random) -> str:
    return f"{rand.choice(_FIRST)} {rand.choice(_LAST)}"

def _next_id(prefix: str) -> str:
    return f"{prefix}-{next(_id_counter)}"

def make_teachers(n: int, rand: random.Random) -> List[Teacher]:
    out = []
    for _ in range(max(0, n)):
        subj = rand.choice(_SUBJECTS)
        out.append(
            Teacher(
                _name(rand),
                _next_id("T"),
                str(rand.randint(900, 2500)),
                rand.choice(_DEPARTMENTS),
                subj,
            )
        )
    return out

def make_assistants(n: int, rand: random.Random) -> List[Assistant]:
    out = []
    for _ in range(max(0, n)):
        out.append(
            Assistant(
                _name(rand),
                _next_id("A"),
                str(rand.randint(600, 1600)),
                rand.choice(_DEPARTMENTS),
            )
        )
    return out

def make_students(n: int, rand: random.Random) -> List[Student]:
    out = []
    for _ in range(max(0, n)):
        grade = f"{rand.randint(1, 10)}"
        spec = rand.choice(_SPECIALITIES)
        out.append(
            Student(
                _name(rand),
                _next_id("S"),
                grade,
                spec,
            )
        )
    return out

def synthesize(counts: Dict[str, int], seed: int | None = None) -> Dict[str, List[object]]:
    rand = random.Random(seed)
    return {
        "Teacher": make_teachers(counts.get("Teacher", 0), rand),
        "Assistant": make_assistants(counts.get("Assistant", 0), rand),
        "Student": make_students(counts.get("Student", 0), rand),
    }
