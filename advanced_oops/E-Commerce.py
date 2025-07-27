# E-Commerce Product Management System with @property

class Product:
    _allowed_categories = ['Electronics', 'Clothing', 'Books', 'Home', 'Sports']

    def __init__(self, name, base_price, discount_percent, stock_quantity, category):
        self.name = name
        self.base_price = base_price
        self.discount_percent = discount_percent
        self.stock_quantity = stock_quantity
        self.category = category

    # name property
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        import re
        if not (3 <= len(value) <= 50):
            raise ValueError("Name must be between 3 and 50 characters.")
        if not re.match(r'^[A-Za-z0-9\- ]+$', value):
            raise ValueError("Name can only contain letters, numbers, hyphens, and spaces.")
        self._name = value

    # base_price property
    @property
    def base_price(self):
        return self._base_price

    @base_price.setter
    def base_price(self, value):
        if not (isinstance(value, (int, float)) and value > 0):
            raise ValueError("Base price must be a positive number.")
        if value > 50000:
            raise ValueError("Base price cannot exceed $50,000.")
        self._base_price = float(value)

    # discount_percent property
    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        if not (isinstance(value, (int, float)) and 0 <= value <= 75):
            raise ValueError("Discount percent must be between 0 and 75.")
        self._discount_percent = round(float(value), 2)

    # stock_quantity property
    @property
    def stock_quantity(self):
        return self._stock_quantity

    @stock_quantity.setter
    def stock_quantity(self, value):
        if not (isinstance(value, int) and value >= 0):
            raise ValueError("Stock quantity must be a non-negative integer.")
        if value > 10000:
            raise ValueError("Stock quantity cannot exceed 10,000 units.")
        self._stock_quantity = value

    # category property
    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if value not in self._allowed_categories:
            raise ValueError(f"Category must be one of {self._allowed_categories}.")
        self._category = value

    # Calculated properties
    @property
    def final_price(self):
        return round(self.base_price * (1 - self.discount_percent / 100), 2)

    @property
    def savings_amount(self):
        return round(self.base_price - self.final_price, 2)

    @property
    def availability_status(self):
        if self.stock_quantity == 0:
            return "Out of Stock"
        elif self.stock_quantity < 10:
            return "Low Stock"
        else:
            return "In Stock"

    @property
    def product_summary(self):
        return (
            f"Product: {self.name}\n"
            f"Category: {self.category}\n"
            f"Base Price: ${self.base_price:.2f}\n"
            f"Discount: {self.discount_percent:.2f}%\n"
            f"Final Price: ${self.final_price:.2f}\n"
            f"Savings: ${self.savings_amount:.2f}\n"
            f"Stock: {self.stock_quantity} units ({self.availability_status})"
        )

# Example usage:
if __name__ == "__main__":
    p = Product(
        name="Wireless Mouse",
        base_price=1200,
        discount_percent=10,
        stock_quantity=5,
        category="Electronics"
    )
    print(p.product_summary)
