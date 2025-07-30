# main.py

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Optional, Dict
from enum import Enum
from decimal import Decimal, ROUND_HALF_UP

app = FastAPI()

class FoodCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main_course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SALAD = "salad"

def round_decimal(val):
    return Decimal(val).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

class FoodItem(BaseModel):
    id: int
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: FoodCategory
    price: Decimal = Field(..., gt=0, max_digits=5, decimal_places=2)
    is_available: bool = True
    preparation_time: int = Field(..., ge=1, le=120)
    ingredients: List[str] = Field(..., min_items=1)
    calories: Optional[int] = Field(None, gt=0)
    is_vegetarian: bool = False
    is_spicy: bool = False

    @validator("name")
    def name_no_numbers_or_special(cls, v):
        import re
        if not re.fullmatch(r"[A-Za-z ]+", v):
            raise ValueError("Name must contain only letters and spaces")
        return v

    @validator("price")
    def price_range(cls, v):
        if not (Decimal("1.00") <= v <= Decimal("100.00")):
            raise ValueError("Price must be between $1.00 and $100.00")
        return round_decimal(v)

    @validator("ingredients")
    def ingredients_not_empty(cls, v):
        if not v or not all(isinstance(i, str) and i.strip() for i in v):
            raise ValueError("At least one ingredient required")
        return v

    @root_validator
    def custom_validations(cls, values):
        category = values.get("category")
        is_spicy = values.get("is_spicy")
        is_vegetarian = values.get("is_vegetarian")
        calories = values.get("calories")
        preparation_time = values.get("preparation_time")

        # Desserts and beverages cannot be spicy
        if category in [FoodCategory.DESSERT, FoodCategory.BEVERAGE] and is_spicy:
            raise ValueError("Desserts and beverages cannot be marked as spicy")

        # Vegetarian calories < 800
        if calories is not None and is_vegetarian and calories >= 800:
            raise ValueError("Vegetarian items must have calories < 800")

        # Beverages prep time <= 10
        if category == FoodCategory.BEVERAGE and preparation_time > 10:
            raise ValueError("Preparation time for beverages must be ≤ 10 minutes")

        return values

    @property
    def price_category(self) -> str:
        if self.price < Decimal("10.00"):
            return "Budget"
        elif self.price <= Decimal("25.00"):
            return "Mid-range"
        else:
            return "Premium"

    @property
    def dietary_info(self) -> List[str]:
        info = []
        if self.is_vegetarian:
            info.append("Vegetarian")
        if self.is_spicy:
            info.append("Spicy")
        return info

    class Config:
        orm_mode = True

# In-memory "database"
menu_db: Dict[int, FoodItem] = {}

# Auto-increment ID
def get_next_id():
    if menu_db:
        return max(menu_db.keys()) + 1
    return 1

# Sample data
sample_menu_items = [
    {
        "name": "Margherita Pizza",
        "description": "Classic pizza with tomato sauce, mozzarella cheese, and fresh basil.",
        "category": "main_course",
        "price": 15.99,
        "preparation_time": 20,
        "ingredients": ["pizza dough", "tomato sauce", "mozzarella", "basil", "olive oil"],
        "calories": 650,
        "is_vegetarian": True,
        "is_spicy": False
    },
    {
        "name": "Spicy Chicken Wings",
        "description": "Crispy chicken wings tossed in our signature hot sauce.",
        "category": "appetizer",
        "price": 12.50,
        "preparation_time": 15,
        "ingredients": ["chicken wings", "hot sauce", "butter", "celery salt"],
        "calories": 420,
        "is_vegetarian": False,
        "is_spicy": True
    },
    {
        "name": "Chocolate Lava Cake",
        "description": "Warm chocolate cake with a gooey molten center.",
        "category": "dessert",
        "price": 8.00,
        "preparation_time": 12,
        "ingredients": ["chocolate", "flour", "eggs", "sugar", "butter"],
        "calories": 550,
        "is_vegetarian": True,
        "is_spicy": False
    },
    {
        "name": "Caesar Salad",
        "description": "Fresh romaine lettuce with Caesar dressing, croutons, and parmesan.",
        "category": "salad",
        "price": 9.50,
        "preparation_time": 10,
        "ingredients": ["romaine lettuce", "croutons", "parmesan", "Caesar dressing"],
        "calories": 320,
        "is_vegetarian": False,
        "is_spicy": False
    },
    {
        "name": "Iced Lemon Tea",
        "description": "Refreshing cold beverage with lemon and tea.",
        "category": "beverage",
        "price": 4.25,
        "preparation_time": 5,
        "ingredients": ["tea", "lemon", "ice", "sugar"],
        "calories": 90,
        "is_vegetarian": True,
        "is_spicy": False
    }
]

# Populate sample data
for item in sample_menu_items:
    item_id = get_next_id()
    menu_db[item_id] = FoodItem(id=item_id, **item)

# API Endpoints

@app.get("/menu", response_model=List[FoodItem])
def get_menu():
    return list(menu_db.values())

@app.get("/menu/{item_id}", response_model=FoodItem)
def get_menu_item(item_id: int):
    item = menu_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@app.post("/menu", response_model=FoodItem, status_code=status.HTTP_201_CREATED)
def add_menu_item(item: FoodItem):
    if item.id in menu_db:
        raise HTTPException(status_code=400, detail="ID already exists")
    menu_db[item.id] = item
    return item

@app.put("/menu/{item_id}", response_model=FoodItem)
def update_menu_item(item_id: int, item: FoodItem):
    if item_id not in menu_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    if item.id != item_id:
        raise HTTPException(status_code=400, detail="ID in path and body must match")
    menu_db[item_id] = item
    return item

@app.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(item_id: int):
    if item_id not in menu_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    del menu_db[item_id]
    return

@app.get("/menu/category/{category}", response_model=List[FoodItem])
def get_menu_by_category(category: FoodCategory):
    return [item for item in menu_db.values() if item.category == category]

# Computed properties endpoints (optional, for demonstration)
@app.get("/menu/{item_id}/price_category")
def get_price_category(item_id: int):
    item = menu_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"price_category": item.price_category}

@app.get("/menu/{item_id}/dietary_info")
def get_dietary_info(item_id: int):
    item = menu_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"dietary_info": item.dietary_info}
