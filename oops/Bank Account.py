# bank_account_management_system.py

class BankAccount:
    _bank_name = "National Bank"
    _min_balance = 0
    _account_count = 0

    @classmethod
    def set_bank_name(cls, name):
        cls._bank_name = name

    @classmethod
    def set_min_balance(cls, amount):
        cls._min_balance = amount

    @classmethod
    def get_bank_name(cls):
        return cls._bank_name

    @classmethod
    def get_account_count(cls):
        return cls._account_count

    def __init__(self, account_id, holder_name, balance):
        if not holder_name or balance < self._min_balance:
            raise ValueError("Invalid account details")
        self._account_id = account_id
        self._holder_name = holder_name
        self._balance = balance
        BankAccount._account_count += 1

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._balance - amount < self._min_balance:
            return False
        self._balance -= amount
        return True

    def get_balance(self):
        return self._balance

    def get_account_id(self):
        return self._account_id

    def get_holder_name(self):
        return self._holder_name

    def display(self):
        print(f"Account ID: {self._account_id}")
        print(f"Holder Name: {self._holder_name}")
        print(f"Balance: {self._balance}")
        print(f"Bank: {self._bank_name}")

class SavingsAccount(BankAccount):
    def __init__(self, account_id, holder_name, balance, interest_rate):
        super().__init__(account_id, holder_name, balance)
        if interest_rate < 0:
            raise ValueError("Interest rate must be non-negative")
        self._interest_rate = interest_rate

    def calculate_monthly_interest(self):
        return self._balance * (self._interest_rate / 100) / 12

    def display(self):
        super().display()
        print(f"Interest Rate: {self._interest_rate}%")

class CheckingAccount(BankAccount):
    def __init__(self, account_id, holder_name, balance, overdraft_limit):
        super().__init__(account_id, holder_name, balance)
        if overdraft_limit < 0:
            raise ValueError("Overdraft limit must be non-negative")
        self._overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self._balance + self._overdraft_limit < amount:
            return False
        self._balance -= amount
        return True

    def display(self):
        super().display()
        print(f"Overdraft Limit: {self._overdraft_limit}")

# Test Cases

print("Test Case 1:")
savings = SavingsAccount("SA001", "Alice Johnson", 1000, 2.5)
checking = CheckingAccount("CA001", "Bob Smith", 500, 200)
savings.display()
print()
checking.display()
print("\n" + "-"*40)

print("Test Case 2:")
print("Savings balance before deposit:", savings.get_balance())
savings.deposit(500)
print("Savings balance after deposit:", savings.get_balance())
result = savings.withdraw(200)
print("Withdrawal of 200 successful?", result)
print("Savings balance after withdrawal:", savings.get_balance())
print("\n" + "-"*40)

print("Test Case 3:")
print("Checking balance:", checking.get_balance())
result = checking.withdraw(600)
print("Overdraft withdrawal of 600 successful?", result)
print("Checking balance after overdraft:", checking.get_balance())
print("\n" + "-"*40)

print("Test Case 4:")
interest = savings.calculate_monthly_interest()
print("Monthly interest earned on savings:", round(interest, 2))
print("\n" + "-"*40)

print("Test Case 5:")
print("Total accounts created:", BankAccount.get_account_count())
print("Bank name:", BankAccount.get_bank_name())
print("\n" + "-"*40)

print("Change Bank Settings:")
BankAccount.set_bank_name("New National Bank")
BankAccount.set_min_balance(100)
print("Bank name changed to:", BankAccount.get_bank_name())
print("Minimum balance set to:", BankAccount._min_balance)
print("\n" + "-"*40)

print("Test Case 6:")
try:
    invalid = SavingsAccount("SA002", "", -100, 1.5)
except ValueError as ve:
    print("Validation error:", ve)
