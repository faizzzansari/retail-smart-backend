from database import products_collection
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from models.product import ProductCreate
from database import db
from datetime import datetime

router = APIRouter()

LOW_STOCK_LIMIT = 5

@router.post("/add-product")
def add_product(product: ProductCreate):

    # Check if SKU already exists
    existing = db.products.find_one({"sku": product.sku})
    if existing:
        raise HTTPException(status_code=400, detail="SKU already exists")

    product_dict = product.dict()
    product_dict["created_at"] = datetime.utcnow()

    result = db.products.insert_one(product_dict)

    return {
        "message": "Product added successfully",
        "id": str(result.inserted_id)
    }

@router.get("/products")
def get_products():
    products = list(db.products.find())

    response = []

    for product in products:
        margin = ((product["selling_price"] - product["cost_price"]) 
                  / product["cost_price"]) * 100

        response.append({
            "id": str(product["_id"]),
            "name": product["name"],
            "sku": product["sku"],
            "barcode": product.get("barcode"),
            "category": product["category"],
            "cost_price": product["cost_price"],
            "selling_price": product["selling_price"],
            "margin": round(margin, 2),
            "stock": product["stock"],
            "minimum_stock_alert": product["minimum_stock_alert"],
            "description": product.get("description"),
            "image_url": product.get("image_url"),
            "created_at": product["created_at"]
        })

    return response

@router.delete("/delete-product/{product_id}")
def delete_product(product_id: str):
    products_collection.delete_one({"_id": ObjectId(product_id)})
    return {"message": "Product deleted"}

@router.get("/low-stock")
def low_stock_products():
    products = list(db.products.find())

    low_stock = []

    for product in products:
        if product["stock"] <= product["minimum_stock_alert"]:
            low_stock.append({
                "id": str(product["_id"]),
                "name": product["name"],
                "stock": product["stock"],
                "minimum_stock_alert": product["minimum_stock_alert"]
            })

    return low_stock