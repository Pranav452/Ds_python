# student_course_management.py

class Student:
    _student_count = 0
    def __init__(self, name, program):
        self.name = name
        self.program = program
        self.courses = {}  # course: grade
        Student._student_count += 1

    def enroll(self, course):
        return course.add_student(self)

    def add_grade(self, course, grade):
        if course in self.courses:
            self.courses[course] = grade
            course.add_grade(self, grade)
        else:
            raise Exception(f"{self.name} is not enrolled in {course.title}")

    def calculate_gpa(self):
        if not self.courses:
            return 0.0
        total = 0
        count = 0
        for grade in self.courses.values():
            if grade is not None:
                total += grade
                count += 1
        return round(total / count, 2) if count else 0.0

    def transcript(self):
        lines = [f"Transcript for {self.name}:"]
        for course, grade in self.courses.items():
            lines.append(f"{course.title}: {grade if grade is not None else 'N/A'}")
        lines.append(f"GPA: {self.calculate_gpa()}")
        return "\n".join(lines)

    @classmethod
    def total_students(cls):
        return cls._student_count

    def __repr__(self):
        return f"{self.name} ({self.program})"


class Course:
    def __init__(self, title, instructor, limit):
        self.title = title
        self.instructor = instructor
        self.limit = limit
        self.students = []
        self.waitlist = []
        self.grades = {}  # student: grade

    def add_student(self, student):
        if student in self.students or student in self.waitlist:
            return f"{student.name} is already enrolled or waitlisted in {self.title}."
        if len(self.students) < self.limit:
            self.students.append(student)
            student.courses[self] = None
            return f"{student.name} enrolled in {self.title}."
        else:
            self.waitlist.append(student)
            return f"{self.title} is full. {student.name} added to waitlist."

    def add_grade(self, student, grade):
        if student in self.students:
            self.grades[student] = grade
        else:
            raise Exception(f"{student.name} is not enrolled in {self.title}")

    def available_spots(self):
        return self.limit - len(self.students)

    def enrollment_count(self):
        return len(self.students)

    def course_statistics(self):
        grades = [g for g in self.grades.values() if g is not None]
        avg = round(sum(grades) / len(grades), 2) if grades else 0.0
        return {
            "title": self.title,
            "instructor": self.instructor,
            "enrolled": len(self.students),
            "waitlist": len(self.waitlist),
            "average_grade": avg
        }

    def __repr__(self):
        return f"{self.title} ({self.instructor})"


class University:
    def __init__(self):
        self.students = []
        self.courses = []

    def add_student(self, student):
        self.students.append(student)

    def add_course(self, course):
        self.courses.append(course)

    def total_enrollments(self):
        return sum(len(course.students) for course in self.courses)

    def average_gpa(self):
        gpas = [s.calculate_gpa() for s in self.students if s.courses]
        return round(sum(gpas) / len(gpas), 2) if gpas else 0.0

    def top_students(self, n=1):
        students_with_gpa = [(s, s.calculate_gpa()) for s in self.students if s.courses]
        students_with_gpa.sort(key=lambda x: x[1], reverse=True)
        return students_with_gpa[:n]


# --- Example Usage (as per your image description) ---

# Create courses
math_course = Course("Calculus I", "Dr. Smith", 30)
physics_course = Course("Physics I", "Dr. Johnson", 25)
cs_course = Course("Programming Basics", "Prof. Brown", 20)

print("Available spots in math course:", math_course.available_spots())

# Create students
student1 = Student("Alice Wilson", "Computer Science")
student2 = Student("Bob Davis", "Mathematics")
student3 = Student("Carol Lee", "Physics")

print("Total students:", Student.total_students())

# University instance for analytics
uni = University()
for s in [student1, student2, student3]:
    uni.add_student(s)
for c in [math_course, physics_course, cs_course]:
    uni.add_course(c)

# Enroll students
print(student1.enroll(math_course))
print(student2.enroll(cs_course))
print("Math course enrollment count:", math_course.enrollment_count())

# Add grades and calculate GPA
student1.add_grade(math_course, 90)
student1.enroll(cs_course)
student1.add_grade(cs_course, 85)
print("Alice's GPA:", student1.calculate_gpa())
print(student1.transcript())

# Course statistics
math_course.add_grade(student2, 80)
print("Math course stats:", math_course.course_statistics())

# University-wide analytics
print("Total enrollments:", uni.total_enrollments())
print("Average GPA:", uni.average_gpa())
print("Top 2 students:", uni.top_students(2))

# Enrollment limits and waitlist
for i in range(25):
    s = Student(f"Student{i+4}", "General")
    uni.add_student(s)
    print(s.enroll(math_course))
print("Waitlist count for math course:", len(math_course.waitlist))
