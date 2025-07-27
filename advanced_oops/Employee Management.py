# Employee Management System with Class Variables and Methods

import re
from datetime import datetime

class Employee:
    # Class variables
    company_name = "Multinational Corp"
    total_employees = 0
    departments = {}  # e.g., {"HR": 2, "Engineering": 5}
    tax_rates = {"USA": 0.2, "India": 0.1, "UK": 0.25}
    next_employee_id = 1
    approved_departments = ["HR", "Engineering", "Sales", "Marketing", "Finance", "Support"]

    def __init__(self, name, department, base_salary, country, email, hire_date=None):
        if not Employee.is_valid_department(department):
            raise ValueError(f"Invalid department: {department}")
        if not Employee.validate_email(email):
            raise ValueError(f"Invalid email: {email}")

        self.employee_id = Employee.generate_employee_id()
        self.name = name
        self.department = department
        self.base_salary = float(base_salary)
        self.country = country
        self.email = email
        self.hire_date = hire_date if hire_date else datetime.now().strftime("%Y-%m-%d")
        self.performance_ratings = []

        # Update class variables
        Employee.total_employees += 1
        Employee.departments[department] = Employee.departments.get(department, 0) + 1

    # ---------- Static Methods ----------
    @staticmethod
    def validate_email(email):
        # Simple regex for email validation and domain check
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email) is not None

    @staticmethod
    def calculate_tax(salary, country):
        rate = Employee.tax_rates.get(country, 0)
        return salary * rate

    @staticmethod
    def is_valid_department(dept):
        return dept in Employee.approved_departments

    @staticmethod
    def generate_employee_id():
        year = datetime.now().year
        eid = f"EMP-{year}-{str(Employee.next_employee_id).zfill(4)}"
        Employee.next_employee_id += 1
        return eid

    # ---------- Class Methods ----------
    @classmethod
    def from_csv_data(cls, csv_line):
        # Format: "name,dept,salary,country,email"
        parts = [x.strip() for x in csv_line.split(",")]
        if len(parts) != 5:
            raise ValueError("CSV line must have 5 fields")
        name, dept, salary, country, email = parts
        return cls(name, dept, salary, country, email)

    @classmethod
    def get_department_stats(cls):
        stats = {}
        for dept in cls.approved_departments:
            stats[dept] = cls.departments.get(dept, 0)
        return stats

    @classmethod
    def set_tax_rate(cls, country, rate):
        cls.tax_rates[country] = rate

    @classmethod
    def hire_bulk_employees(cls, employee_list):
        # employee_list: list of csv lines
        new_employees = []
        for line in employee_list:
            try:
                emp = cls.from_csv_data(line)
                new_employees.append(emp)
            except Exception as e:
                print(f"Error hiring employee from line '{line}': {e}")
        return new_employees

    # ---------- Instance Methods ----------
    def add_performance_rating(self, rating):
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        self.performance_ratings.append(rating)

    def get_average_performance(self):
        if not self.performance_ratings:
            return 0
        return sum(self.performance_ratings) / len(self.performance_ratings)

    def calculate_net_salary(self):
        tax = Employee.calculate_tax(self.base_salary, self.country)
        return self.base_salary - tax

    def get_years_of_service(self):
        hire = datetime.strptime(self.hire_date, "%Y-%m-%d")
        now = datetime.now()
        years = (now - hire).days / 365.25
        return years

    def is_eligible_for_bonus(self):
        return self.get_average_performance() > 3.5 and self.get_years_of_service() > 1

# ------------------- Example Usage / Test Cases -------------------

if __name__ == "__main__":
    # Single employee
    emp1 = Employee("Alice", "Engineering", 80000, "USA", "alice@company.com", "2022-07-01")
    emp1.add_performance_rating(4)
    emp1.add_performance_rating(5)
    print(emp1.employee_id)  # e.g., EMP-2025-0001
    print(emp1.get_average_performance())  # 4.5
    print(emp1.calculate_net_salary())  # 64000.0
    print(emp1.get_years_of_service())  # e.g., 3.07
    print(emp1.is_eligible_for_bonus())  # True

    # Bulk hire
    csv_lines = [
        "Bob,HR,50000,India,bob@company.com",
        "Carol,Sales,60000,UK,carol@company.com",
        "Dave,Engineering,90000,USA,dave@company.com"
    ]
    employees = Employee.hire_bulk_employees(csv_lines)
    for emp in employees:
        emp.add_performance_rating(3)
        emp.add_performance_rating(4)
        print(emp.name, emp.employee_id, emp.calculate_net_salary())

    # Department stats
    print(Employee.get_department_stats())  # {'HR': 1, 'Engineering': 2, ...}

    # Set new tax rate
    Employee.set_tax_rate("India", 0.12)
    print(Employee.tax_rates)

    # Email validation
    print(Employee.validate_email("test@domain.com"))  # True
    print(Employee.validate_email("bademail.com"))     # False
