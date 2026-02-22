from pydantic import BaseModel
from typing import Optional, List

class SaleItem(BaseModel):
    product_id: str
    quantity: int

class SaleCreate(BaseModel):
    items: List[SaleItem]

    customer_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

    payment_method: str
    amount_tendered: Optional[float] = 0

    discount_type: Optional[str] = None  # percentage / flat
    discount_value: Optional[float] = 0
    discount_reason: Optional[str] = None

    tax_percentage: float = 0