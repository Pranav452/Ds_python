# data_processing_enumerate.py

students = ["Alice", "Bob", "Carol", "David", "Eve"]
scores = [85, 92, 78, 88, 95]

# 1. Create a Numbered List of Students
print("Numbered List of Students:")
for i, name in enumerate(students, start=1):
    print(f"{i}. {name}")
print()

# 2. Pair Students with Their Scores Using enumerate()
print("Students with their Scores:")
for i, name in enumerate(students):
    print(f"{name}: {scores[i]}")
print()

# 3. Find Positions of High Scorers (score > 90)
print("Positions of High Scorers (score > 90):")
for i, score in enumerate(scores):
    if score > 90:
        print(i)
print()

# 4. Map Positions to Student Names
position_to_name = {i: name for i, name in enumerate(students)}
print("Dictionary mapping positions to student names:")
print(position_to_name)
