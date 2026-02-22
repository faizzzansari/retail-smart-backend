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
    # Date Range Logic
    # ----------------------------------
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date) + timedelta(days=1)
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
    # Metrics Calculation
    # ----------------------------------
    total_sales = 0
    total_profit = 0
    total_transactions = len(sales)

    product_summary = {}
    trend = {}

    for sale in sales:

        # ✅ Use stored total directly
        sale_total = sale.get("total", 0)
        total_sales += sale_total

        # ✅ Trend grouping
        created_at = sale.get("created_at")
        if created_at:
            date_key = created_at.strftime("%Y-%m-%d")
            trend[date_key] = trend.get(date_key, 0) + sale_total

        # ✅ Loop items
        for item in sale.get("items", []):

            quantity = item.get("quantity", 0)

            # ✅ Use stored total from item (VERY IMPORTANT)
            item_total = item.get("total", 0)
            cost_price = item.get("cost_price", 0)

            revenue = item_total
            cost = quantity * cost_price
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

            product_summary[pid]["quantity"] += quantity
            product_summary[pid]["revenue"] += revenue
            product_summary[pid]["profit"] += profit

    avg_order_value = (
        total_sales / total_transactions if total_transactions else 0
    )

    profit_margin = (
        (total_profit / total_sales) * 100 if total_sales else 0
    )

    sales_trend = [
        {"date": k, "total": round(v, 2)}
        for k, v in sorted(trend.items())
    ]

    top_products = sorted(
        product_summary.values(),
        key=lambda x: x["quantity"],
        reverse=True
    )[:5]