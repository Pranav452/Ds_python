# inventory_management.py

# 1. Initial inventory
inventory = {
    "apples": {"price": 10, "quantity": 150},
    "bananas": {"price": 5, "quantity": 200}
}

# 2. Add a new product
inventory["oranges"] = {"price": 8, "quantity": 120}

# 3. Update product price
inventory["bananas"]["price"] = 6

# 4. Sell 25 apples
inventory["apples"]["quantity"] -= 25

# 5. Calculate total inventory value
total_value = 0
for product in inventory.values():
    total_value += product["price"] * product["quantity"]
print("Total Inventory Value:", total_value)

# 6. Find low stock products
print("Low stock products:")
for name, product in inventory.items():
    if product["quantity"] < 100:
        print(name)
