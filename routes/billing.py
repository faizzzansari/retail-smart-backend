from fastapi import APIRouter, HTTPException
from database import db
from models.sale import SaleCreate
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/create-sale")
def create_sale(sale: SaleCreate):

    subtotal = 0
    updated_items = []

    for item in sale.items:
        product = db.products.find_one({"_id": ObjectId(item.product_id)})

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product["stock"] < item.quantity:
            raise HTTPException(status_code=400, detail="Insufficient stock")

        line_total = product["selling_price"] * item.quantity
        subtotal += line_total

        # Reduce stock
        db.products.update_one(
            {"_id": ObjectId(item.product_id)},
            {"$inc": {"stock": -item.quantity}}
        )

        updated_items.append({
            "product_id": item.product_id,
            "name": product["name"],
            "price": product["selling_price"],
            "quantity": item.quantity,
            "line_total": line_total
        })

    # Apply Discount
    discount_amount = 0

    if sale.discount_type == "percentage":
        discount_amount = (subtotal * sale.discount_value) / 100
    elif sale.discount_type == "flat":
        discount_amount = sale.discount_value

    subtotal_after_discount = subtotal - discount_amount

    # Apply Tax
    tax_amount = (subtotal_after_discount * sale.tax_percentage) / 100
    final_total = subtotal_after_discount + tax_amount

    if sale.phone:

        existing_customer = db.customers.find_one({"phone": sale.phone})

        if existing_customer:
            db.customers.update_one(
                {"_id": existing_customer["_id"]},
                {
                    "$inc": {
                        "visit_count": 1,
                        "total_purchases": final_total
                    },
                    "$set": {
                        "last_visit": datetime.utcnow(),
                        "name": sale.customer_name,
                        "email": sale.email
                    }
                }
            )
        else:
            db.customers.insert_one({
                "name": sale.customer_name,
                "phone": sale.phone,
                "email": sale.email,
                "visit_count": 1,
                "total_purchases": final_total,
                "last_visit": datetime.utcnow(),
                "created_at": datetime.utcnow()
            })

    sale_data = {
        "items": updated_items,
        "customer_name": sale.customer_name,
        "phone": sale.phone,
        "email": sale.email,
        "payment_method": sale.payment_method,
        "amount_tendered": sale.amount_tendered,
        "discount_type": sale.discount_type,
        "discount_value": sale.discount_value,
        "discount_reason": sale.discount_reason,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "tax_amount": tax_amount,
        "total": final_total,
        "created_at": datetime.utcnow()
    }

    result = db.sales.insert_one(sale_data)

    return {
        "message": "Sale created successfully",
        "sale_id": str(result.inserted_id),
        "total": final_total
    }

@router.get("/customers/frequent")
def get_frequent_customers():

    customers = list(
        db.customers
        .find()
        .sort("visit_count", -1)
        .limit(10)
    )

    result = []

    for c in customers:
        result.append({
            "id": str(c["_id"]),
            "name": c["name"],
            "phone": c["phone"],
            "email": c.get("email"),
            "visit_count": c["visit_count"],
            "total_purchases": c["total_purchases"]
        })

    return result

@router.get("/customers/search")
def search_customer(phone: str):

    customer = db.customers.find_one({"phone": phone})

    if not customer:
        return {"message": "Customer not found"}

    return {
        "id": str(customer["_id"]),
        "name": customer["name"],
        "phone": customer["phone"],
        "email": customer.get("email"),
        "visit_count": customer["visit_count"],
        "total_purchases": customer["total_purchases"]
    }