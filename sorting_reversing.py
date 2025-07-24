# sorting_reversing.py

# Sample employee data: (name, salary, department)
employees = [
    ("Alice", 70000, "HR"),
    ("Bob", 50000, "Engineering"),
    ("Charlie", 60000, "Engineering"),
    ("David", 55000, "Marketing"),
    ("Eve", 65000, "HR"),
    ("Frank", 48000, "Marketing"),
]

# 1. Sort by Salary (ascending)
employees_by_salary_asc = sorted(employees, key=lambda x: x[1])
print("Sorted by salary (ascending):")
print(employees_by_salary_asc)
print()

# 1. Sort by Salary (descending)
employees_by_salary_desc = sorted(employees, key=lambda x: x[1], reverse=True)
print("Sorted by salary (descending):")
print(employees_by_salary_desc)
print()

# 2. Sort by Department, then by Salary
employees_by_dept_salary = sorted(employees, key=lambda x: (x[2], x[1]))
print("Sorted by department, then by salary:")
print(employees_by_dept_salary)
print()

# 3. Create a Reversed List (without modifying original)
employees_reversed = list(reversed(employees))
print("Reversed list (original not modified):")
print(employees_reversed)
print()

# 4. Sort by Name Length
employees_by_name_length = sorted(employees, key=lambda x: len(x[0]))
print("Sorted by name length:")
print(employees_by_name_length)
print()

# 5. Demonstrate .sort() vs sorted()
# Using .sort() (modifies original)
employees_copy = employees.copy()
employees_copy.sort(key=lambda x: x[1])  # Sort by salary ascending
print("Using .sort() (modifies list):")
print(employees_copy)
print()

# Using sorted() (does not modify original)
employees_sorted = sorted(employees, key=lambda x: x[1])
print("Using sorted() (original list unchanged):")
print(employees_sorted)
print("Original list:")
print(employees)
