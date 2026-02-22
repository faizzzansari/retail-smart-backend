from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    sku: str
    barcode: Optional[str] = None
    category: str

    cost_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)

    stock: int = Field(..., ge=0)
    minimum_stock_alert: int = Field(..., ge=0)

    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductResponse(BaseModel):
    id: str
    name: str
    sku: str
    barcode: Optional[str]
    category: str

    cost_price: float
    selling_price: float
    margin: float

    stock: int
    minimum_stock_alert: int

    description: Optional[str]
    image_url: Optional[str]

    created_at: datetime