# student_records.py

# List of student records as tuples: (student_id, name, grade, age)
students = [
    (101, "Alice", 85, 20),
    (102, "Bob", 92, 21),
    (103, "Carol", 78, 21),
    (104, "David", 88, 20),
]

# 1. Find the Student with the Highest Grade
# Start by assuming the first student has the highest grade
top_student = students[0]
for student in students:
    if student[2] > top_student[2]:  # Compare grades (index 2)
        top_student = student

print("Student with the highest grade:")
print("ID:", top_student[0])
print("Name:", top_student[1])
print("Grade:", top_student[2])
print("Age:", top_student[3])

# 2. Create a Name-Grade List
name_grade_list = []
for student in students:
    name_grade = (student[1], student[2])  # (name, grade)
    name_grade_list.append(name_grade)

print("\nName-Grade List:")
print(name_grade_list)

# 3. Demonstrate Tuple Immutability
print("\nDemonstrating tuple immutability:")
try:
    # Attempt to change the grade of the first student
    students[0][2] = 90
except TypeError as e:
    print("Error:", e)
    print("Tuples are immutable, so you cannot change their values after creation.")
    print("This is why tuples are preferred for records like student data, where you want to prevent accidental changes.")

# End of file
