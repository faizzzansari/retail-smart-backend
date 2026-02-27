from database import products_collection
from bson import ObjectId
from fastapi import APIRouter, HTTPException, UploadFile, File
from models.product import ProductCreate
from database import db
from datetime import datetime
import shutil
import os

router = APIRouter()

LOW_STOCK_LIMIT = 5

@router.post("/add-product")
def add_product(product: ProductCreate, email: str):

    user = db.users.find_one({"email": email})

    if not user or user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only admin can add products")

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

@router.put("/update-product/{product_id}")
def update_product(product_id: str, product: ProductCreate):

    # Check if valid ObjectId
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    existing_product = db.products.find_one({"_id": ObjectId(product_id)})

    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Prevent duplicate SKU (if changed)
    sku_check = db.products.find_one({
        "sku": product.sku,
        "_id": {"$ne": ObjectId(product_id)}
    })

    if sku_check:
        raise HTTPException(status_code=400, detail="SKU already exists")

    updated_data = product.dict()
    updated_data["updated_at"] = datetime.utcnow()

    db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": updated_data}
    )

    return {
        "message": "Product updated successfully",
        "id": product_id
    }

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    
    file_location = f"static/images/{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "image_url": f"/static/images/{file.filename}"
    }

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