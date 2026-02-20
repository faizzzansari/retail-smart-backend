from fastapi import APIRouter
from database import products_collection
from bson import ObjectId
from models import Product

router = APIRouter()

LOW_STOCK_LIMIT = 5

@router.post("/add-product")
def add_product(product: Product):
    product_dict = product.dict()
    result = products_collection.insert_one(product_dict)
    return {"message": "Product added", "id": str(result.inserted_id)}

@router.get("/products")
def get_products():
    products = []
    for product in products_collection.find():
        product["_id"] = str(product["_id"])
        products.append(product)
    return products

# @router.get("/products")
# def get_products():
#     products = []
#     for product in products_collection.find():
#         product["id"] = str(product["_id"])
#         del product["_id"]
#         products.append(product)
#     return products

@router.delete("/delete-product/{product_id}")
def delete_product(product_id: str):
    products_collection.delete_one({"_id": ObjectId(product_id)})
    return {"message": "Product deleted"}

@router.get("/low-stock")
def get_low_stock_products():
    low_stock_products = []

    for product in products_collection.find({"stock": {"$lte": LOW_STOCK_LIMIT}}):
        product["id"] = str(product["_id"])
        del product["_id"]
        low_stock_products.append(product)

    return {
        "threshold": LOW_STOCK_LIMIT,
        "low_stock_count": len(low_stock_products),
        "products": low_stock_products
    }