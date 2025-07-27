# Advanced Vehicle Fleet Management with Inheritance

from datetime import datetime

class MaintenanceRecord:
    def __init__(self):
        self.records = []  # Each record: (date, description, mileage)

    def add_record(self, description, mileage):
        record = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'description': description,
            'mileage': mileage
        }
        self.records.append(record)

    def get_records(self):
        return self.records

class Vehicle(MaintenanceRecord):
    def __init__(self, vehicle_id, make, model, year, daily_rate, mileage, fuel_type):
        super().__init__()
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.year = year
        self.daily_rate = daily_rate
        self.is_available = True
        self.mileage = mileage
        self.fuel_type = fuel_type

    def rent(self):
        if self.is_available:
            self.is_available = False
            return True
        return False

    def return_vehicle(self, new_mileage):
        self.is_available = True
        self.mileage = new_mileage

    def calculate_rental_cost(self, days):
        return self.daily_rate * days

    def get_vehicle_info(self):
        return {
            'vehicle_id': self.vehicle_id,
            'make': self.make,
            'model': self.model,
            'year': self.year,
            'daily_rate': self.daily_rate,
            'is_available': self.is_available,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type
        }

    def fuel_efficiency(self):
        # Placeholder: override in subclasses
        return None

class Car(Vehicle):
    def __init__(self, vehicle_id, make, model, year, daily_rate, mileage, fuel_type,
                 seating_capacity, transmission_type, has_gps):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        self.seating_capacity = seating_capacity
        self.transmission_type = transmission_type
        self.has_gps = has_gps

    def calculate_rental_cost(self, days):
        multiplier = 1.2 if self.has_gps else 1.1
        return round(self.daily_rate * days * multiplier, 2)

    def fuel_efficiency(self):
        # Example: cars average 15 km/l
        return 15

class Motorcycle(Vehicle):
    def __init__(self, vehicle_id, make, model, year, daily_rate, mileage, fuel_type,
                 engine_cc, bike_type):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        self.engine_cc = engine_cc
        self.bike_type = bike_type

    def calculate_rental_cost(self, days):
        multiplier = 1.05 if self.bike_type == 'sport' else 1.0
        return round(self.daily_rate * days * multiplier, 2)

    def fuel_efficiency(self):
        # Example: motorcycles average 35 km/l
        return 35

class Truck(Vehicle):
    def __init__(self, vehicle_id, make, model, year, daily_rate, mileage, fuel_type,
                 cargo_capacity, license_required, max_weight):
        super().__init__(vehicle_id, make, model, year, daily_rate, mileage, fuel_type)
        self.cargo_capacity = cargo_capacity
        self.license_required = license_required
        self.max_weight = max_weight

    def calculate_rental_cost(self, days):
        multiplier = 1.5 if self.max_weight > 5000 else 1.3
        return round(self.daily_rate * days * multiplier, 2)

    def fuel_efficiency(self):
        # Example: trucks average 8 km/l
        return 8

# Example usage and test cases

if __name__ == "__main__":
    car = Car("C001", "Toyota", "Camry", 2022, 100, 20000, "Petrol", 5, "Automatic", True)
    bike = Motorcycle("M001", "Yamaha", "R15", 2021, 50, 5000, "Petrol", 155, "sport")
    truck = Truck("T001", "Volvo", "FH", 2020, 300, 80000, "Diesel", 20000, "Heavy", 12000)

    # Rent vehicles
    print(car.rent())  # True
    print(car.rent())  # False (already rented)
    car.return_vehicle(20200)
    print(car.is_available)  # True

    # Rental cost
    print(car.calculate_rental_cost(3))  # Car with GPS
    print(bike.calculate_rental_cost(2))  # Sport bike
    print(truck.calculate_rental_cost(1))  # Heavy truck

    # Maintenance
    car.add_record("Oil change", 20200)
    print(car.get_records())

    # Fuel efficiency
    print(car.fuel_efficiency())    # 15
    print(bike.fuel_efficiency())   # 35
    print(truck.fuel_efficiency())  # 8

    # Vehicle info
    print(car.get_vehicle_info())
