# sales_data_analysis.py

sales_data = [
    [("Jan", 1000), ("Feb", 1200), ("Mar", 1100)],
    [("Apr", 1300), ("May", 1250), ("Jun", 1400)],
    [("Jul", 1500), ("Aug", 1600), ("Sep", 1550)]
]

# 1. Total sales per quarter
print("Total sales per quarter:")
quarter_number = 1
for quarter in sales_data:
    total = 0
    for month, sales in quarter:
        total += sales
    print("Quarter", quarter_number, ":", total)
    quarter_number += 1

print()

# 2. Find the month with highest sales (using single-line if-else)
highest_sales = 0
highest_month = ""
for quarter in sales_data:
    for month, sales in quarter:
        highest_month, highest_sales = (month, sales) if sales > highest_sales else (highest_month, highest_sales)
print("Month with highest sales:", highest_month, "(", highest_sales, ")")

print()

# 3. Create a flat list of monthly sales
flat_list = []
for quarter in sales_data:
    for month, sales in quarter:
        flat_list.append((month, sales))
print("Flat list of monthly sales:")
print(flat_list)

print()

# 4. Use unpacking in loops (showing month, sales, and quarter)
print("All sales data (with unpacking):")
quarter_number = 1
for quarter in sales_data:
    print("Quarter", quarter_number)
    for month, sales in quarter:
        print("  Month:", month, "Sales:", sales)
    quarter_number += 1
