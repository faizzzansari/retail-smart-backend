from fastapi import APIRouter, Query
from datetime import datetime, timedelta
from database import db

router = APIRouter()

@router.get("/reports")
def get_reports(
    period: str = Query("daily"),
    start_date: str = Query(None),
    end_date: str = Query(None)
):
    now = datetime.utcnow()

    # ----------------------------------
    # Custom Range Has Highest Priority
    # ----------------------------------
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date) + timedelta(days=1)

    # ----------------------------------
    # Otherwise Use Period
    # ----------------------------------
    else:
        if period == "daily":
            start = datetime(now.year, now.month, now.day)
            end = start + timedelta(days=1)

        elif period == "weekly":
            start = now - timedelta(days=7)
            end = now

        elif period == "monthly":
            start = now - timedelta(days=30)
            end = now

        else:
            return {"error": "Invalid period"}

    # ----------------------------------
    # Fetch Sales
    # ----------------------------------
    sales = list(db.sales.find({
        "created_at": {"$gte": start, "$lte": end}
    }))

    # ----------------------------------
    # If No Sales
    # ----------------------------------
    if not sales:
        return {
            "metrics": {
                "total_sales": 0,
                "transactions": 0,
                "average_order_value": 0,
                "total_profit": 0,
                "profit_margin": 0
            },
            "sales_trend": [],
            "top_products": []
        }

    # ----------------------------------
    # Calculate Metrics
    # ----------------------------------
    total_sales = sum(s.get("total_amount", 0) for s in sales)
    total_transactions = len(sales)
    avg_order_value = total_sales / total_transactions if total_transactions else 0

    total_profit = 0
    product_summary = {}
    trend = {}

    for sale in sales:

        # Trend grouping
        date_key = sale["created_at"].strftime("%Y-%m-%d")
        trend[date_key] = trend.get(date_key, 0) + sale.get("total_amount", 0)

        for item in sale.get("items", []):
            revenue = item.get("total", 0)
            cost = item.get("cost_price", 0) * item.get("quantity", 0)
            profit = revenue - cost
            total_profit += profit

            pid = str(item.get("product_id"))

            if pid not in product_summary:
                product_summary[pid] = {
                    "name": item.get("name"),
                    "quantity": 0,
                    "revenue": 0,
                    "profit": 0
                }

            product_summary[pid]["quantity"] += item.get("quantity", 0)
            product_summary[pid]["revenue"] += revenue
            product_summary[pid]["profit"] += profit

    profit_margin = (total_profit / total_sales * 100) if total_sales else 0

    sales_trend = [
        {"date": k, "total": v}
        for k, v in sorted(trend.items())
    ]

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