from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from database import db

router = APIRouter()

@router.get("/reports")
def get_reports(
    period: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    now = datetime.utcnow()

    # ---------------------------
    # Determine Date Range
    # ---------------------------
    if period == "daily":
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1)

    elif period == "weekly":
        start = now - timedelta(days=7)
        end = now

    elif period == "monthly":
        start = now - timedelta(days=30)
        end = now

    elif start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)

    else:
        return {"error": "Provide period or start_date & end_date"}

    # ---------------------------
    # Fetch Sales
    # ---------------------------
    sales = list(db.sales.find({
        "created_at": {"$gte": start, "$lte": end}
    }))

    if not sales:
        return {
            "metrics": {},
            "sales_trend": [],
            "top_products": []
        }

    # ---------------------------
    # Calculate Metrics
    # ---------------------------
    total_sales = sum(s["total_amount"] for s in sales)
    total_transactions = len(sales)
    avg_order_value = total_sales / total_transactions if total_transactions else 0

    total_profit = 0
    product_summary = {}

    for sale in sales:
        for item in sale["items"]:
            revenue = item["total"]
            cost = item["cost_price"] * item["quantity"]
            profit = revenue - cost
            total_profit += profit

            pid = str(item["product_id"])

            if pid not in product_summary:
                product_summary[pid] = {
                    "name": item["name"],
                    "quantity": 0,
                    "revenue": 0,
                    "profit": 0
                }

            product_summary[pid]["quantity"] += item["quantity"]
            product_summary[pid]["revenue"] += revenue
            product_summary[pid]["profit"] += profit

    profit_margin = (total_profit / total_sales * 100) if total_sales else 0

    # ---------------------------
    # Sales Trend (Group by Date)
    # ---------------------------
    trend = {}

    for sale in sales:
        date_key = sale["created_at"].strftime("%Y-%m-%d")

        if date_key not in trend:
            trend[date_key] = 0

        trend[date_key] += sale["total_amount"]

    sales_trend = [
        {"date": k, "total": v}
        for k, v in sorted(trend.items())
    ]

    # ---------------------------
    # Top Selling Products
    # ---------------------------
    top_products = sorted(
        product_summary.values(),
        key=lambda x: x["quantity"],
        reverse=True
    )[:5]

    return {
        "metrics": {
            "total_sales": round(total_sales, 2),
            "transactions": total_transactions,
            "average_order_value": round(avg_order_value, 2),
            "total_profit": round(total_profit, 2),
            "profit_margin": round(profit_margin, 2)
        },
        "sales_trend": sales_trend,
        "top_products": top_products
    }