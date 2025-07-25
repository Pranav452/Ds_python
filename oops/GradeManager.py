from collections import defaultdict

class GradeManager:
    def __init__(self):
        # Each student maps to a dict of subjects and their scores
        self.grades = defaultdict(dict)

    def add_grade(self, student, subject, score):
        """
        Adds or updates the score for a student in a subject.
        """
        self.grades[student][subject] = score

    def get_grades(self, student):
        """
        Returns a dict of subjects and scores for the given student.
        If the student does not exist, returns an empty dict.
        """
        return self.grades.get(student, {})

    def get_average(self, student):
        """
        Returns the average score for the given student.
        If the student does not exist or has no grades, returns None.
        """
        subjects = self.grades.get(student)
        if not subjects:
            return None
        return sum(subjects.values()) / len(subjects)

    def get_all_students(self):
        """
        Returns a list of all student names.
        """
        return list(self.grades.keys())

# Example usage:
if __name__ == "__main__":
    gm = GradeManager()
    gm.add_grade("Alice", "Math", 90)
    gm.add_grade("Alice", "Science", 85)
    gm.add_grade("Bob", "Math", 78)
    gm.add_grade("Bob", "English", 88)
    gm.add_grade("Charlie", "Math", 95)

    print("Alice's grades:", gm.get_grades("Alice"))
    print("Bob's average:", gm.get_average("Bob"))
    print("All students:", gm.get_all_students())
