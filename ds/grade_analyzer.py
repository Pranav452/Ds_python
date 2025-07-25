# grade_analyzer.py

grades = [85, 92, 78, 90, 88, 76, 94, 89, 87, 91]

# 1. Slice grades from index 2 to 7 (index 2 included, 7 excluded)
sliced_grades = grades[2:7]
print("Sliced grades (index 2 to 6):", sliced_grades)

# 2. Use list comprehension to find grades above 85
grades_above_85 = [grade for grade in grades if grade > 85]
print("Grades above 85:", grades_above_85)

# 3. Replace the grade at index 3 with 95
grades[3] = 95
print("After replacing index 3 with 95:", grades)

# 4. Append three new grades
grades.append(80)
grades.append(99)
grades.append(77)
print("After appending three new grades:", grades)

# 5. Sort in descending order and display the top 5 grades
grades_sorted = sorted(grades, reverse=True)
top_5_grades = grades_sorted[:5]
print("Top 5 grades (descending):", top_5_grades)
