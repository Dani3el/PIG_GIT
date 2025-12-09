from typing import List
from data.db import Database
from model.teacher import Teacher
from model.assistant import Assistant
from model.student import Student
from repository._helpers import _to_float, _to_int

class SchoolRepository:
    def __init__(self, db: Database):
        self.db = db

    # ---------- Teacher ----------
    def add_teacher(self, t: Teacher) -> None:
        self.db.execute(
            "INSERT INTO teacher(id,name,salary,department,subject) VALUES(?,?,?,?,?)",
            (t.id, t.name, _to_float(t.salary, "Salary"), t.department, t.subject),
        )

    def update_teacher(self, t: Teacher) -> bool:
        self.db.execute(
            "UPDATE teacher SET name=?, salary=?, department=?, subject=? WHERE id=?",
            (t.name, _to_float(t.salary, "Salary"), t.department, t.subject, t.id),
        )
        return True

    def update_teacher_by_id(self, old_id: str, t: Teacher) -> bool:
        self.db.execute(
            "UPDATE teacher SET id=?, name=?, salary=?, department=?, subject=? WHERE id=?",
            (t.id, t.name, _to_float(t.salary, "Salary"), t.department, t.subject, old_id),
        )
        return True

    def delete_teacher(self, id_: str) -> bool:
        self.db.execute("DELETE FROM teacher WHERE id=?", (id_,))
        return True

    def list_teachers(self) -> List[Teacher]:
        rows = self.db.query("SELECT id,name,salary,department,subject FROM teacher ORDER BY name")
        return [Teacher(r[1], r[0], str(r[2]), r[3], r[4]) for r in rows]

    # ---------- Assistant ----------
    def add_assistant(self, a: Assistant) -> None:
        self.db.execute(
            "INSERT INTO assistant(id,name,salary,department) VALUES(?,?,?,?)",
            (a.id, a.name, _to_float(a.salary, "Salary"), a.department),
        )

    def update_assistant(self, a: Assistant) -> bool:
        self.db.execute(
            "UPDATE assistant SET name=?, salary=?, department=? WHERE id=?",
            (a.name, _to_float(a.salary, "Salary"), a.department, a.id),
        )
        return True

    def update_assistant_by_id(self, old_id: str, a: Assistant) -> bool:
        self.db.execute(
            "UPDATE assistant SET id=?, name=?, salary=?, department=? WHERE id=?",
            (a.id, a.name, _to_float(a.salary, "Salary"), a.department, old_id),
        )
        return True

    def delete_assistant(self, id_: str) -> bool:
        self.db.execute("DELETE FROM assistant WHERE id=?", (id_,))
        return True

    def list_assistants(self) -> List[Assistant]:
        rows = self.db.query("SELECT id,name,salary,department FROM assistant ORDER BY name")
        return [Assistant(r[1], r[0], str(r[2]), r[3]) for r in rows]

    # ---------- Student ----------
    def add_student(self, s: Student) -> None:
        self.db.execute(
            "INSERT INTO student(id,name,grade,speciality) VALUES(?,?,?,?)",
            (s.id, s.name, _to_int(s.grade, "Grade"), s.speciality),
        )

    def update_student(self, s: Student) -> bool:
        self.db.execute(
            "UPDATE student SET name=?, grade=?, speciality=? WHERE id=?",
            (s.name, _to_int(s.grade, "Grade"), s.speciality, s.id),
        )
        return True

    def update_student_by_id(self, old_id: str, s: Student) -> bool:
        self.db.execute(
            "UPDATE student SET id=?, name=?, grade=?, speciality=? WHERE id=?",
            (s.id, s.name, _to_int(s.grade, "Grade"), s.speciality, old_id),
        )
        return True

    def delete_student(self, id_: str) -> bool:
        self.db.execute("DELETE FROM student WHERE id=?", (id_,))
        return True

    def list_students(self) -> List[Student]:
        rows = self.db.query("SELECT id,name,grade,speciality FROM student ORDER BY name")
        return [Student(r[1], r[0], str(r[2]), r[3]) for r in rows]

    # ---------- Aggregations for charts ----------
    def counts_by_role(self) -> list[tuple[str,int]]:
        t = self.db.scalar("SELECT COUNT(*) FROM teacher") or 0
        a = self.db.scalar("SELECT COUNT(*) FROM assistant") or 0
        s = self.db.scalar("SELECT COUNT(*) FROM student") or 0
        return [("Teacher", t), ("Assistant", a), ("Student", s)]

    def students_by_speciality(self) -> list[tuple[str,int]]:
        return self.db.query(
            "SELECT speciality, COUNT(*) FROM student GROUP BY speciality ORDER BY COUNT(*) DESC, speciality ASC"
        )

    def avg_salary_by_department(self) -> list[tuple[str,float]]:
        return self.db.query(
            """
            SELECT department, AVG(salary) AS avg_sal FROM (
                SELECT department, salary FROM teacher
                UNION ALL
                SELECT department, salary FROM assistant
            ) x GROUP BY department ORDER BY avg_sal DESC, department ASC
            """
        )

    def teachers_by_subject(self) -> list[tuple[str,int]]:
        return self.db.query(
            "SELECT subject, COUNT(*) FROM teacher GROUP BY subject ORDER BY COUNT(*) DESC, subject ASC"
        )

    def salaries_series(self) -> list[float]:
        rows = self.db.query("SELECT salary FROM teacher UNION ALL SELECT salary FROM assistant")
        return [float(r[0]) for r in rows]

    def student_grades_series(self) -> list[int]:
        rows = self.db.query("SELECT grade FROM student")
        return [int(r[0]) for r in rows]

    def salary_by_department_groups(self) -> list[tuple[str, list[float]]]:
        rows = self.db.query(
            """
            SELECT department, salary FROM (
                SELECT department, salary FROM teacher
                UNION ALL
                SELECT department, salary FROM assistant
            )
            ORDER BY department
            """
        )
        groups: dict[str, list[float]] = {}
        for dep, sal in rows:
            groups.setdefault(dep, []).append(float(sal))
        return sorted(groups.items(), key=lambda x: x[0])

    # ---------- DB normalization (defensive) ----------
    def normalize_db_values(self) -> None:
        for t in self.list_teachers():
            self.db.execute(
                "UPDATE teacher SET name=?, salary=?, department=?, subject=? WHERE id=?",
                (t.name, _to_float(t.salary, "Salary"), t.department, t.subject, t.id),
            )
        for a in self.list_assistants():
            self.db.execute(
                "UPDATE assistant SET name=?, salary=?, department=? WHERE id=?",
                (a.name, _to_float(a.salary, "Salary"), a.department, a.id),
            )
        for s in self.list_students():
            self.db.execute(
                "UPDATE student SET name=?, grade=?, speciality=? WHERE id=?",
                (s.name, _to_int(s.grade, "Grade"), s.speciality, s.id),
            )
