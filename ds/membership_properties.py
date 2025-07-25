# membership_properties.py

# 1. Define the data structures
fruits_list = ["apple", "banana", "cherry", "orange"]
fruits_tuple = ("apple", "banana", "cherry", "orange")
fruits_set = {"apple", "banana", "cherry", "orange"}
fruits_dict = {"apple": 5, "banana": 3, "cherry": 7, "orange": 2}

# 2. Check for Membership
print("Membership Test for 'apple':")
print("In list:", "apple" in fruits_list)
print("In tuple:", "apple" in fruits_tuple)
print("In set:", "apple" in fruits_set)
print("In dict (keys):", "apple" in fruits_dict)
print()

# 3. Find Length
print("Length of each data structure:")
print("List:", len(fruits_list))
print("Tuple:", len(fruits_tuple))
print("Set:", len(fruits_set))
print("Dict:", len(fruits_dict))
print()

# 4. Iterate and Print Elements
print("Iterating through list:")
for fruit in fruits_list:
    print(fruit)
print()

print("Iterating through tuple:")
for fruit in fruits_tuple:
    print(fruit)
print()

print("Iterating through set:")
for fruit in fruits_set:
    print(fruit)
print()

print("Iterating through dict (keys):")
for fruit in fruits_dict:
    print(fruit)
print()

print("Iterating through dict (key-value pairs):")
for fruit, count in fruits_dict.items():
    print(fruit, ":", count)
print()

# 5. Compare Membership Testing Performance
print("Performance Explanation:")
print(
    "Sets and dictionaries provide faster membership testing (O(1) on average) "
    "because they use hash tables. Lists and tuples require checking each element one by one (O(n))."
)
