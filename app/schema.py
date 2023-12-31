from pydantic import BaseModel, Field
from typing import List
from datetime import datetime, timezone, timedelta
from enum import Enum

class UserCredentials(BaseModel):
    username: str
    password: str

class Permission(BaseModel):
    name: str
    read: bool
    write: bool
    description: str

class Role(BaseModel):
    name: str
    description: str
    permission: List[Permission]

class User(UserCredentials):
    name: str
    role: int = 0 

class GetUser(BaseModel):
    name: str
    username: str

class Product(BaseModel):
    name: str
    price: float
    category: str
    quantity: int

class Category(BaseModel):
    name: str

class PaymentType(str, Enum):
    cash = "Cash"
    transfer = "Transfer"
    pos = "POS"
    debt = "Debt"

class OrderType(str, Enum):
    instant_order = "Instant Order"
    shipment = "Shipment"

class Order(BaseModel):
    items: List[Product]
    customer: str
    orderType: OrderType = OrderType.instant_order
    receiptNo: int
    createdAt: datetime = datetime.now(timezone(timedelta(hours=1)))
    createdBy: str = Field(None, alias='createdBy')
    revoked: bool = False
    paymentType: PaymentType = PaymentType.cash
    paidTotal: int
    qtySold: int
    totalSale: int

    class Config:
        allow_populate_by_field_name = True
        arbitrary_types_allowed = True