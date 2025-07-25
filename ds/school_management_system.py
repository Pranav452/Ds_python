# school_management_system.py

school = {
    "ClassA": {
        "teacher": "Mrs. Smith",
        "students": {
            "Alice": 85,
            "Bob": 92,
            "Charlie": 78
        }
    },
    "ClassB": {
        "teacher": "Mr. Johnson",
        "students": {
            "David": 88,
            "Eva": 95,
            "Frank": 80
        }
    },
    "ClassC": {
        "teacher": "Ms. Lee",
        "students": {
            "Grace": 90,
            "Helen": 87,
            "Ian": 93
        }
    }
}

# 1. Print Teacher Names
print("Teacher Names:")
for class_info in school.values():
    print(class_info["teacher"])
print()

# 2. Calculate Class Average Grades
print("Class Average Grades:")
for class_name, class_info in school.items():
    grades = list(class_info["students"].values())
    avg_grade = sum(grades) / len(grades)
    print(f"{class_name}: {avg_grade:.2f}")
print()

# 3. Find Top Student Across All Classes
top_student = None
top_grade = -1
for class_info in school.values():
    for student_name, grade in class_info["students"].items():
        if grade > top_grade:
            top_grade = grade
            top_student = student_name

print(f"Top Student Across All Classes: {top_student} with grade {top_grade}")
print()

# 4. Use Unpacking to Work with Student Names and Grades
print("Student Names and Grades (using unpacking):")
for class_name, class_info in school.items():
    print(f"{class_name}:")
    for student_name, grade in class_info["students"].items():
        # Unpacking student_name and grade
        name, score = student_name, grade
        print(f"  {name}: {score}")
