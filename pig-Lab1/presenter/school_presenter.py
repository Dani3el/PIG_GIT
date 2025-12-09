from typing import Dict, List, Tuple
from model.teacher import Teacher
from model.student import Student
from model.assistant import Assistant
from model.stats import StatsModel
from model.faker import synthesize
from data.db import Database
from repository.school_repository import SchoolRepository

class SchoolPresenter:
    def __init__(
        self,
        initial_counts: dict | None = None,
        seed: int | None = None,
        database_url: str = "",
    ):
        self.view = None
        self._stats = StatsModel()
        self._db = Database(database_url)
        self._repo = SchoolRepository(self._db)

        # sortare curentă (Name | Grade | Salary) — fără “Role”
        self._sort_mode = "Name"

        try:
            self._repo.normalize_db_values()
        except Exception:
            pass

        counts = {"Teacher": 0, "Assistant": 0, "Student": 0}
        for role, c in self._repo.counts_by_role():
            counts[role] = c
        if sum(counts.values()) == 0:
            default_counts = {"Teacher": 4, "Assistant": 3, "Student": 12}
            to_make = default_counts if initial_counts is None else initial_counts
            self._seed_random(to_make, seed=seed)

    def set_view(self, view) -> None:
        self.view = view

    def get_db_path(self) -> str:
        p = self._db.sqlite_path()
        return p or "(PostgreSQL connection)"

    # ------------ Sorting (fără Role) ------------
    def get_sort_options(self) -> list[str]:
        return ["Name", "Grade", "Salary"]

    def set_sort_mode(self, label: str) -> None:
        m = (label or "").strip().lower()
        if m == "name":
            self._sort_mode = "Name"
        elif m == "grade":
            self._sort_mode = "Grade"
        elif m == "salary":
            self._sort_mode = "Salary"
        else:
            self._sort_mode = "Name"

    # ------------ CRUD ------------
    def add_person(self, person_type: str, values: dict) -> Tuple[bool, str]:
        try:
            if person_type == "Teacher":
                obj = Teacher(values["Name"], values["ID"], values["Salary"], values["Department"], values["Subject"])
                self._repo.add_teacher(obj)
            elif person_type == "Student":
                obj = Student(values["Name"], values["ID"], values["Grade"], values["Speciality"])
                self._repo.add_student(obj)
            elif person_type == "Assistant":
                obj = Assistant(values["Name"], values["ID"], values["Salary"], values["Department"])
                self._repo.add_assistant(obj)
            else:
                return False, f"Invalid person type: {person_type}"
            return True, f"Added {person_type}: {values['Name']}"
        except Exception as e:
            return False, f"Error adding {person_type}: {e}"

    def edit_person(self, person_type: str, name: str, values: dict) -> Tuple[bool, str]:
        try:
            all_data = self._snapshot()
            target = next((o for o in all_data.get(person_type, []) if getattr(o, "name", "") == name), None)
            if not target:
                return False, f"{person_type} '{name}' not found"

            if person_type == "Teacher":
                target.name = values.get("Name", target.name)
                target.id = values.get("ID", target.id)
                target.salary = values.get("Salary", target.salary)
                target.department = values.get("Department", target.department)
                target.subject = values.get("Subject", target.subject)
                self._repo.update_teacher(target)

            elif person_type == "Student":
                target.name = values.get("Name", target.name)
                target.id = values.get("ID", target.id)
                target.grade = values.get("Grade", target.grade)
                target.speciality = values.get("Speciality", target.speciality)
                self._repo.update_student(target)

            else:  # Assistant
                target.name = values.get("Name", target.name)
                target.id = values.get("ID", target.id)
                target.salary = values.get("Salary", target.salary)
                target.department = values.get("Department", target.department)
                self._repo.update_assistant(target)

            return True, f"Edited {person_type}: {target.name}"
        except Exception as e:
            return False, f"Error editing {person_type}: {e}"

    def delete_person(self, person_type: str, name: str) -> Tuple[bool, str]:
        try:
            all_data = self._snapshot()
            target = next((o for o in all_data.get(person_type, []) if getattr(o, "name", "") == name), None)
            if not target:
                return False, f"{person_type} '{name}' not found"

            if person_type == "Teacher":
                self._repo.delete_teacher(target.id)
            elif person_type == "Student":
                self._repo.delete_student(target.id)
            else:
                self._repo.delete_assistant(target.id)

            return True, f"Deleted {person_type}: {name}"
        except Exception as e:
            return False, f"Error deleting {person_type}: {e}"

    # ------------ ID-centric ------------
    def find_by_id(self, person_type: str, id_: str):
        snap = self._snapshot()
        for obj in snap.get(person_type, []):
            if getattr(obj, "id", None) == id_:
                return obj
        return None

    def delete_by_id(self, person_type: str, id_: str) -> Tuple[bool, str]:
        try:
            if person_type == "Teacher":
                self._repo.delete_teacher(id_)
            elif person_type == "Student":
                self._repo.delete_student(id_)
            elif person_type == "Assistant":
                self._repo.delete_assistant(id_)
            else:
                return False, f"Invalid person type: {person_type}"
            return True, f"Deleted {person_type} id={id_}"
        except Exception as e:
            return False, f"Error deleting {person_type} id={id_}: {e}"

    def edit_by_id(self, person_type: str, id_: str, values: dict) -> Tuple[bool, str]:
        obj = self.find_by_id(person_type, id_)
        if not obj:
            return False, f"{person_type} id={id_} not found"
        try:
            if person_type == "Teacher":
                obj.name = values.get("Name", obj.name)
                obj.id = values.get("ID", obj.id)
                obj.salary = values.get("Salary", obj.salary)
                obj.department = values.get("Department", obj.department)
                obj.subject = values.get("Subject", obj.subject)
                self._repo.update_teacher(obj)

            elif person_type == "Student":
                obj.name = values.get("Name", obj.name)
                obj.id = values.get("ID", obj.id)
                obj.grade = values.get("Grade", obj.grade)
                obj.speciality = values.get("Speciality", obj.speciality)
                self._repo.update_student(obj)

            else:  # Assistant
                obj.name = values.get("Name", obj.name)
                obj.id = values.get("ID", obj.id)
                obj.salary = values.get("Salary", obj.salary)
                obj.department = values.get("Department", obj.department)
                self._repo.update_assistant(obj)

            return True, f"Edited {person_type}: {obj.name}"
        except Exception as e:
            return False, f"Error editing {person_type} id={id_}: {e}"

    def apply_changes(self, person_type: str, original_id: str, values: dict) -> Tuple[bool, str, str]:
        obj = self.find_by_id(person_type, original_id)
        if not obj:
            return False, f"{person_type} id={original_id} not found", original_id

        try:
            new_id = values.get("ID", getattr(obj, "id", original_id)) or original_id
            new_name = values.get("Name", getattr(obj, "name", ""))

            if person_type == "Teacher":
                obj.id = new_id
                obj.name = new_name
                obj.salary = values.get("Salary", getattr(obj, "salary", "0"))
                obj.department = values.get("Department", getattr(obj, "department", ""))
                obj.subject = values.get("Subject", getattr(obj, "subject", ""))
                self._repo.update_teacher_by_id(original_id, obj)

            elif person_type == "Student":
                obj.id = new_id
                obj.name = new_name
                obj.grade = values.get("Grade", getattr(obj, "grade", "0"))
                obj.speciality = values.get("Speciality", getattr(obj, "speciality", ""))
                self._repo.update_student_by_id(original_id, obj)

            elif person_type == "Assistant":
                obj.id = new_id
                obj.name = new_name
                obj.salary = values.get("Salary", getattr(obj, "salary", "0"))
                obj.department = values.get("Department", getattr(obj, "department", ""))
                self._repo.update_assistant_by_id(original_id, obj)

            else:
                return False, f"Invalid person type: {person_type}", original_id

            return True, f"Saved {person_type}: {new_name}", new_id
        except Exception as e:
            return False, f"Error saving {person_type} id={original_id}: {e}", original_id

    # ------------ Fields ------------
    def validate_fields(self, values: dict) -> bool:
        for k, v in values.items():
            if not str(v).strip():
                return False
        if "Grade" in values:
            _ = int(str(values["Grade"]).strip())
        if "Salary" in values:
            _ = float(str(values["Salary"]).strip().replace(",", "."))
        return True

    def get_field_definitions(self, person_type: str) -> list[tuple]:
        fields = {
            "Teacher": [
                ("Name", "entry"),
                ("ID", "entry"),
                ("Salary", "entry"),
                ("Department", "optionmenu", ["Human Resources", "Finance", "Engineering", "Marketing"]),
                ("Subject", "optionmenu", ["Mathematics", "Physics", "Chemistry", "Biology"]),
            ],
            "Student": [
                ("Name", "entry"),
                ("ID", "entry"),
                ("Grade", "entry"),
                ("Speciality", "optionmenu", ["Computer Science", "Mathematics", "Physics", "Engineering"]),
            ],
            "Assistant": [
                ("Name", "entry"),
                ("ID", "entry"),
                ("Salary", "entry"),
                ("Department", "optionmenu", ["Human Resources", "Finance", "Engineering", "Marketing"]),
            ],
        }
        return fields.get(person_type, [])

    # ------------ Charts ------------
    def get_chart_types(self) -> list[str]:
        return [
            "Roles Distribution",
            "Students by Speciality",
            "Avg Salary by Department",
            "Teachers by Subject",
            "Student Grades (Series)",
            "All Salaries (Series)",
            "Salary by Department (Groups)",
        ]

    def get_chart_payload(self, chart_type: str) -> dict:
        ct = (chart_type or "").strip().lower()

        if ct == "roles distribution":
            rows = self._repo.counts_by_role()
            return {"type": "categorical", "labels": [r[0] for r in rows], "values": [r[1] for r in rows],
                    "title": "Distribuția rolurilor", "ylabel": "Număr"}

        if ct == "students by speciality":
            rows = self._repo.students_by_speciality()
            return {"type": "categorical", "labels": [r[0] for r in rows], "values": [r[1] for r in rows],
                    "title": "Studenți pe specialitate", "ylabel": "Număr"}

        if ct == "avg salary by department":
            rows = self._repo.avg_salary_by_department()
            return {"type": "categorical", "labels": [r[0] for r in rows], "values": [r[1] for r in rows],
                    "title": "Salariu mediu pe departament", "ylabel": "Salariu mediu"}

        if ct == "teachers by subject":
            rows = self._repo.teachers_by_subject()
            return {"type": "categororical", "labels": [r[0] for r in rows], "values": [r[1] for r in rows],
                    "title": "Profesori pe disciplină", "ylabel": "Număr"}

        if ct == "student grades (series)":
            return {"type": "series", "series": self._repo.student_grades_series(),
                    "title": "Note studenți (serie)", "ylabel": "Notă"}

        if ct == "all salaries (series)":
            return {"type": "series", "series": self._repo.salaries_series(),
                    "title": "Salarii (serie)", "ylabel": "Salariu"}

        if ct == "salary by department (groups)":
            return {"type": "groups", "groups": self._repo.salary_by_department_groups(),
                    "title": "Salarii pe departament (boxplot)", "ylabel": "Salariu"}

        rows = self._repo.counts_by_role()
        return {"type": "categorical", "labels": [r[0] for r in rows], "values": [r[1] for r in rows],
                "title": "Distribuția rolurilor", "ylabel": "Număr"}

    # ------------ Dump ------------
    def get_all_data(self) -> str:
        lines: list[str] = []

        teachers = self._repo.list_teachers()
        lines.append(f"[Teachers] count={len(teachers)}")
        for t in teachers:
            lines.append(f"  - {t.id} | {t.name} | salary={t.salary} | dep={t.department} | subj={t.subject}")

        assistants = self._repo.list_assistants()
        lines.append(f"[Assistants] count={len(assistants)}")
        for a in assistants:
            lines.append(f"  - {a.id} | {a.name} | salary={a.salary} | dep={a.department}")

        students = self._repo.list_students()
        lines.append(f"[Students] count={len(students)}")
        for s in students:
            lines.append(f"  - {s.id} | {s.name} | grade={s.grade} | spec={s.speciality}")

        return "\n".join(lines)

    # ------------ Helpers ------------
    def _snapshot(self) -> Dict[str, List[object]]:
        try:
            teachers = self._repo.list_teachers()
            assistants = self._repo.list_assistants()
            students = self._repo.list_students()

            mode = self._sort_mode
            if mode == "Name":
                key = lambda o: str(getattr(o, "name", "")).casefold()
                teachers.sort(key=key)
                assistants.sort(key=key)
                students.sort(key=key)

            elif mode == "Grade":
                students.sort(key=lambda o: int(getattr(o, "grade", 0)), reverse=True)
                key = lambda o: str(getattr(o, "name", "")).casefold()
                teachers.sort(key=key)
                assistants.sort(key=key)

            elif mode == "Salary":
                teachers.sort(key=lambda o: float(getattr(o, "salary", 0.0)), reverse=True)
                assistants.sort(key=lambda o: float(getattr(o, "salary", 0.0)), reverse=True)
                students.sort(key=lambda o: str(getattr(o, "name", "")).casefold())

            return {"Teacher": teachers, "Assistant": assistants, "Student": students}
        except Exception:
            return {"Teacher": [], "Assistant": [], "Student": []}

    def _seed_random(self, counts: dict, seed: int | None) -> None:
        synth = synthesize(counts, seed=seed)
        for t in synth["Teacher"]:
            self._repo.add_teacher(t)
        for a in synth["Assistant"]:
            self._repo.add_assistant(a)
        for s in synth["Student"]:
            self._repo.add_student(s)
