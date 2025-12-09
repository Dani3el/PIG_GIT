import unittest
from presenter.school_presenter import SchoolPresenter


class TestSchoolPresenter(unittest.TestCase):
    def setUp(self):
        self.presenter = SchoolPresenter()

    def test_delete_existing_person(self):
        # Add a teacher then delete
        success, msg = self.presenter.add_person("Teacher", {
            "Name": "Alice",
            "ID": "T1",
            "Salary": "1000",
            "Department": "Engineering",
            "Subject": "Mathematics"
        })
        self.assertTrue(success, msg)

        success, msg = self.presenter.delete_person("Teacher", "Alice")
        self.assertTrue(success, msg)

        # Ensure it's removed from internal data
        names = [getattr(o, 'name', None) for o in self.presenter.data.get('Teacher', [])]
        self.assertNotIn("Alice", names)

    def test_delete_nonexistent_person(self):
        success, msg = self.presenter.delete_person("Student", "Bob")
        self.assertFalse(success)
        self.assertIn("not found", msg.lower())


if __name__ == "__main__":
    unittest.main()
