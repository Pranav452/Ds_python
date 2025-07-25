# ecommerce_shopping_cart_system.py

class Product:
    def __init__(self, product_id, name, price, category, stock_quantity):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.category = category
        self.stock_quantity = stock_quantity

    def __str__(self):
        return f"{self.name} ({self.category}) - ${self.price:.2f} | Stock: {self.stock_quantity}"

    def reduce_stock(self, quantity):
        if quantity > self.stock_quantity:
            raise ValueError("Not enough stock")
        self.stock_quantity -= quantity

    def increase_stock(self, quantity):
        self.stock_quantity += quantity


class Customer:
    def __init__(self, customer_id, name, email, is_premium=False):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.is_premium = is_premium
        self.orders = []

    def get_discount_rate(self):
        return 0.1 if self.is_premium else 0.0

    def add_order(self, order):
        self.orders.append(order)

    def total_revenue(self):
        return sum(order.total_price for order in self.orders)

    def __str__(self):
        return f"{self.name} ({'Premium' if self.is_premium else 'Regular'})"


class Cart:
    def __init__(self):
        self.items = {}  # product: quantity

    def add_product(self, product, quantity):
        if product in self.items:
            self.items[product] += quantity
        else:
            self.items[product] = quantity

    def remove_product(self, product):
        if product in self.items:
            del self.items[product]

    def clear(self):
        self.items.clear()

    def total_items(self):
        return sum(self.items.values())

    def subtotal(self):
        return sum(product.price * qty for product, qty in self.items.items())

    def __str__(self):
        if not self.items:
            return "Cart is empty."
        return "\n".join([f"{product.name} x {qty}" for product, qty in self.items.items()])


class Order:
    def __init__(self, customer, cart):
        self.customer = customer
        self.items = cart.items.copy()
        self.total_price = self.calculate_total()
        self.completed = False

    def calculate_total(self):
        subtotal = sum(product.price * qty for product, qty in self.items.items())
        discount = subtotal * self.customer.get_discount_rate()
        return round(subtotal - discount, 2)

    def place_order(self):
        # Check stock
        for product, qty in self.items.items():
            if qty > product.stock_quantity:
                return False
        # Reduce stock
        for product, qty in self.items.items():
            product.reduce_stock(qty)
        self.completed = True
        self.customer.add_order(self)
        return True


def most_popular_category(orders):
    from collections import Counter
    category_counter = Counter()
    for order in orders:
        for product, qty in order.items.items():
            category_counter[product.category] += qty
    if not category_counter:
        return None
    return category_counter.most_common(1)[0][0]


# ------------------ TEST CASES ------------------

# Test Case 1: Product creation and info
laptop = Product("P001", "Gaming Laptop", 1299.99, "Electronics", 10)
book = Product("P002", "Python Programming", 49.99, "Books", 25)
shirt = Product("P003", "Cotton T-Shirt", 19.99, "Clothing", 50)
print(laptop)  # Gaming Laptop (Electronics) - $1299.99 | Stock: 10

# Test Case 2: Customer creation and discount
customer = Customer("C001", "John Doe", "john@email.com", is_premium=True)
print(customer)  # John Doe (Premium)
print("Discount rate:", customer.get_discount_rate())  # 0.1

# Test Case 3: Cart operations
cart = Cart()
cart.add_product(laptop, 1)
cart.add_product(book, 2)
cart.add_product(shirt, 1)
print("Cart items:\n", cart)
print("Total items in cart:", cart.total_items())  # 4
print("Subtotal:", cart.subtotal())  # 1299.99 + 2*49.99 + 19.99

# Test Case 4: Order and discount calculation
order = Order(customer, cart)
print("Total price after discount:", order.total_price)  # Should apply 10% discount

# Test Case 5: Inventory update after order
print("Laptop stock before order:", laptop.stock_quantity)  # 10
order_result = order.place_order()
print("Order placed:", order_result)  # True
print("Laptop stock after order:", laptop.stock_quantity)  # 9

# Test Case 6: Business analytics
orders = [order]
print("Most popular category:", most_popular_category(orders))  # Electronics or Books (Books if 2 qty)
print("Total revenue by customer:", customer.total_revenue())  # Should match order.total_price

# Test Case 7: Cart removal and clearing
cart.remove_product(book)
print("Cart after removing book:\n", cart)
print("Total items in cart after removal:", cart.total_items())  # 2
cart.clear()
print("Cart after clearing:\n", cart)  # Cart is empty.
