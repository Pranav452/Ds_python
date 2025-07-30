
# main.py

from fastapi import FastAPI, HTTPException, Path, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator, ValidationError
from typing import List, Dict, Optional
from enum import Enum
import re

app = FastAPI(
    title="Restaurant Ordering System",
    description="API for managing restaurant menu and orders",
    version="1.0.0"
)

# --- In-memory "databases" and ID counters ---
menu_db: Dict[int, "FoodItem"] = {}
orders_db: Dict[int, "Order"] = {}
next_menu_id = 1
next_order_id = 1

# --- Models ---

class FoodItem(BaseModel):
    id: int
    name: str
    price: float = Field(..., gt=0)
    description: Optional[str] = None

class FoodItemCreate(BaseModel):
    name: str
    price: float = Field(..., gt=0)
    description: Optional[str] = None

class FoodItemResponse(FoodItem):
    pass

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    DELIVERED = "DELIVERED"

class OrderItem(BaseModel):
    menu_item_id: int
    menu_item_name: str
    quantity: int = Field(..., ge=1, le=10)
    unit_price: float = Field(..., gt=0)

    @property
    def item_total(self) -> float:
        return self.quantity * self.unit_price

class Customer(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., regex=r"^\d{10}$")
    address: str = Field(..., min_length=1)

class Order(BaseModel):
    id: int
    customer: Customer
    items: List[OrderItem]
    status: OrderStatus = OrderStatus.PENDING

    @property
    def items_total(self) -> float:
        return sum(item.item_total for item in self.items)

    @property
    def total_items_count(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def total_amount(self) -> float:
        delivery_fee = 30.0
        return self.items_total + delivery_fee

    @validator("items")
    def must_have_items(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Order must have at least one item")
        return v

class OrderCreate(BaseModel):
    customer: Customer
    items: List[OrderItem]

class OrderResponse(BaseModel):
    id: int
    customer: Customer
    items: List[OrderItem]
    status: OrderStatus
    items_total: float
    total_items_count: int
    total_amount: float

class OrderSummaryResponse(BaseModel):
    id: int
    customer_name: str
    status: OrderStatus
    total_items_count: int
    total_amount: float

class ErrorResponse(BaseModel):
    detail: str

# --- Exception Handlers ---

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

# --- Menu Endpoints (for completeness) ---

@app.post("/menu", response_model=FoodItemResponse, status_code=201)
def create_menu_item(item: FoodItemCreate):
    global next_menu_id
    food_item = FoodItem(id=next_menu_id, **item.dict())
    menu_db[next_menu_id] = food_item
    next_menu_id += 1
    return food_item

@app.get("/menu", response_model=List[FoodItemResponse])
def get_menu():
    return list(menu_db.values())

@app.get("/menu/{item_id}", response_model=FoodItemResponse)
def get_menu_item(item_id: int = Path(..., gt=0)):
    item = menu_db.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

# --- Orders Endpoints ---

@app.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(order_data: OrderCreate):
    global next_order_id
    # Validate menu items exist and fill in names/prices
    items = []
    for item in order_data.items:
        menu_item = menu_db.get(item.menu_item_id)
        if not menu_item:
            raise HTTPException(status_code=400, detail=f"Menu item ID {item.menu_item_id} does not exist")
        items.append(OrderItem(
            menu_item_id=menu_item.id,
            menu_item_name=menu_item.name,
            quantity=item.quantity,
            unit_price=menu_item.price
        ))
    order = Order(
        id=next_order_id,
        customer=order_data.customer,
        items=items
    )
    orders_db[next_order_id] = order
    next_order_id += 1
    return OrderResponse(
        id=order.id,
        customer=order.customer,
        items=order.items,
        status=order.status,
        items_total=order.items_total,
        total_items_count=order.total_items_count,
        total_amount=order.total_amount
    )

@app.get("/orders", response_model=List[OrderSummaryResponse])
def list_orders():
    return [
        OrderSummaryResponse(
            id=order.id,
            customer_name=order.customer.name,
            status=order.status,
            total_items_count=order.total_items_count,
            total_amount=order.total_amount
        )
        for order in orders_db.values()
    ]

@app.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int = Path(..., gt=0)):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(
        id=order.id,
        customer=order.customer,
        items=order.items,
        status=order.status,
        items_total=order.items_total,
        total_items_count=order.total_items_count,
        total_amount=order.total_amount
    )

class OrderStatusUpdate(BaseModel):
    status: OrderStatus

@app.put("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(order_id: int, status_update: OrderStatusUpdate):
    order = orders_db.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status_update.status
    return OrderResponse(
        id=order.id,
        customer=order.customer,
        items=order.items,
        status=order.status,
        items_total=order.items_total,
        total_items_count=order.total_items_count,
        total_amount=order.total_amount
    )

# --- Root endpoint ---

@app.get("/")
def root():
    return {"message": "Welcome to the Restaurant Ordering System API!"}
