from fastapi import APIRouter, HTTPException
from database import products_collection, sales_collection
from models import SaleRequest
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/create-sale")
def create_sale(sale: SaleRequest):

    subtotal = 0
    sale_items_details = []

    for item in sale.items:

        product = products_collection.find_one({"_id": ObjectId(item.product_id)})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {product['name']}"
            )

        item_total = product["price"] * item.quantity
        subtotal += item_total

        sale_items_details.append({
            "product_id": item.product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "item_total": item_total
        })

        # Reduce stock
        products_collection.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )

    tax_amount = subtotal * (sale.tax_percentage / 100)
    final_total = subtotal + tax_amount

    sale_record = {
        "items": sale_items_details,
        "subtotal": subtotal,
        "tax_percentage": sale.tax_percentage,
        "tax_amount": tax_amount,
        "total": final_total,
        "date": datetime.now()
    }

    result = sales_collection.insert_one(sale_record)

    return {
        "message": "Sale completed successfully",
        "sale_id": str(result.inserted_id),
        "subtotal": subtotal,
        "tax": tax_amount,
        "total": final_total
    }