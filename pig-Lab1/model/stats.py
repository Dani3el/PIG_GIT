# model/stats.py
from typing import Dict, List, Tuple
from model.student import Student
from model.teacher import Teacher
from model.assistant import Assistant

class StatsModel:
    def roles_distribution(self, data: Dict[str, List[object]]) -> List[Tuple[str, int]]:
        return [(role, len(items)) for role, items in data.items()]

    def students_by_speciality(self, data: Dict[str, List[object]]) -> List[Tuple[str, int]]:
        counts: Dict[str, int] = {}
        for obj in data.get("Student", []):
            if isinstance(obj, Student):
                spec = getattr(obj, "speciality", "Unknown")
                counts[spec] = counts.get(spec, 0) + 1
        return sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    def avg_salary_by_department(self, data: Dict[str, List[object]]) -> List[Tuple[str, float]]:
        sums: Dict[str, float] = {}
        counts: Dict[str, int] = {}
        for role in ("Teacher", "Assistant"):
            for obj in data.get(role, []):
                if isinstance(obj, (Teacher, Assistant)):
                    dep = getattr(obj, "department", "Unknown")
                    try:
                        sal = float(getattr(obj, "salary", 0))
                    except (TypeError, ValueError):
                        sal = 0.0
                    sums[dep] = sums.get(dep, 0.0) + sal
                    counts[dep] = counts.get(dep, 0) + 1
        result = []
        for dep, total in sums.items():
            c = counts.get(dep, 1)
            result.append((dep, total / c if c else 0.0))
        return sorted(result, key=lambda x: (-x[1], x[0]))

    def teachers_by_subject(self, data: Dict[str, List[object]]) -> List[Tuple[str, int]]:
        counts: Dict[str, int] = {}
        for obj in data.get("Teacher", []):
            if isinstance(obj, Teacher):
                subj = getattr(obj, "subject", "Unknown")
                counts[subj] = counts.get(subj, 0) + 1
        return sorted(counts.items(), key=lambda x: (-x[1], x[0]))

    def student_grades_series(self, data: Dict[str, List[object]]) -> List[int]:
        vals: List[int] = []
        for obj in data.get("Student", []):
            if isinstance(obj, Student):
                try:
                    vals.append(int(getattr(obj, "grade", 0)))
                except (TypeError, ValueError):
                    pass
        return vals

    def salaries_series(self, data: Dict[str, List[object]]) -> List[float]:
        vals: List[float] = []
        for role in ("Teacher", "Assistant"):
            for obj in data.get(role, []):
                if isinstance(obj, (Teacher, Assistant)):
                    try:
                        vals.append(float(getattr(obj, "salary", 0)))
                    except (TypeError, ValueError):
                        pass
        return vals

    def salary_by_department_groups(self, data: Dict[str, List[object]]) -> List[Tuple[str, List[float]]]:
        groups: Dict[str, List[float]] = {}
        for role in ("Teacher", "Assistant"):
            for obj in data.get(role, []):
                if isinstance(obj, (Teacher, Assistant)):
                    dep = getattr(obj, "department", "Unknown")
                    try:
                        sal = float(getattr(obj, "salary", 0))
                    except (TypeError, ValueError):
                        sal = 0.0
                    groups.setdefault(dep, []).append(sal)
        return sorted(groups.items(), key=lambda x: x[0])
