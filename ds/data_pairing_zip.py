# data_pairing_zip.py

# Example data
products = ["Pen", "Notebook", "Eraser", "Marker", "Pencil"]
prices = [10, 50, 5, 20, 7]
quantities = [100, 50, 200, 8, 5]

# 1. Create Product-Price Pairs
product_price_pairs = list(zip(products, prices))
print("Product-Price Pairs:")
print(product_price_pairs)
print()

# 2. Calculate Total Value for Each Product
print("Total Inventory Value for Each Product:")
for product, price, quantity in zip(products, prices, quantities):
    total_value = price * quantity
    print(f"{product}: {total_value}")
print()

# 3. Build a Product Catalog Dictionary
catalog = {
    product: {"price": price, "quantity": quantity}
    for product, price, quantity in zip(products, prices, quantities)
}
print("Product Catalog Dictionary:")
print(catalog)
print()

# 4. Find Low Stock Products (quantity < 10)
print("Low Stock Products (quantity < 10):")
for product, info in catalog.items():
    if info["quantity"] < 10:
        print(product)
