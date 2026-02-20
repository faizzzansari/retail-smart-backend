from fastapi import APIRouter
from database import sales_collection
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.get("/sales")
def get_all_sales():
    sales = []
    for sale in sales_collection.find().sort("date", -1):
        sale["id"] = str(sale["_id"])
        del sale["_id"]
        sales.append(sale)
    return sales


@router.get("/daily-sales")
def daily_sales():
    today = datetime.now().date()
    total = 0
    count = 0

    for sale in sales_collection.find():
        if sale["date"].date() == today:
            total += sale["total"]
            count += 1

    return {
        "date": str(today),
        "total_sales": total,
        "number_of_transactions": count
    }


@router.get("/monthly-sales")
def monthly_sales():
    now = datetime.now()
    total = 0
    count = 0

    for sale in sales_collection.find():
        sale_date = sale["date"]
        if sale_date.month == now.month and sale_date.year == now.year:
            total += sale["total"]
            count += 1

    return {
        "month": now.strftime("%B"),
        "year": now.year,
        "total_sales": total,
        "number_of_transactions": count
    }