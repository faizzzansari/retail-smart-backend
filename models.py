from pydantic import BaseModel
from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    name: str
    sku: str
    price: float
    stock: int
    category: str


class SaleItem(BaseModel):
    product_id: str
    quantity: int

class SaleRequest(BaseModel):
    items: List[SaleItem]
    tax_percentage: float = 0