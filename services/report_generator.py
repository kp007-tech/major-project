from services.festival_recommender import recommend_festival


from services.festival_recommender import recommend_festival


def _safe_dict(value):
    return value if isinstance(value, dict) else {}


def _safe_list(value):
    return value if isinstance(value, list) else []


def generate_report(data):
    """
    Convert analyzer output into a normalized structure
    for forecasting/report.html and PDF export.
    """
    if not isinstance(data, dict):
        return {"error": "Invalid analysis data"}

    if "error" in data:
        return {"error": data["error"]}

    data_type = data.get("type")

    if data_type == "structured":
        top_selling = _safe_dict(data.get("top_selling"))
        low_selling = _safe_dict(data.get("low_selling"))
        zero_sales = _safe_list(data.get("zero_sales"))
        monthly_sales = _safe_dict(data.get("monthly_sales"))
        all_products = _safe_dict(data.get("all_products"))

        total_products = int(
            data.get("total_products", len(all_products) if all_products else 0)
        )
        total_sales_value = (
            sum(all_products.values())
            if all_products
            else sum(top_selling.values()) + sum(low_selling.values())
        )

        top_products = list(top_selling.keys())
        low_products = list(low_selling.keys())

        return {
            "summary": f"{total_products} products analyzed successfully.",
            "details": {
                "top_selling": top_selling,
                "low_selling": low_selling,
                "zero_sales": zero_sales,
                "total_products": total_products,
                "total_sales_value": round(float(total_sales_value), 2),
                "monthly_sales": monthly_sales,
                "all_products": all_products,
                "content_preview": "",
            },
            "recommendation": {
                "buy_more": top_products,
                "avoid": low_products,
                "festival": recommend_festival(top_products),
            },
        }

    if data_type == "text":
        content_preview = str(data.get("content", ""))[:1000]

        return {
            "summary": "PDF analyzed successfully.",
            "details": {
                "top_selling": {},
                "low_selling": {},
                "zero_sales": [],
                "total_products": 0,
                "total_sales_value": 0,
                "monthly_sales": {},
                "all_products": {},
                "content_preview": content_preview,
            },
            "recommendation": {
                "buy_more": [],
                "avoid": [],
                "festival": "Needs structured sales data for better recommendations.",
            },
        }

    if data_type == "zip":
        results = data.get("results", [])

        combined_top = {}
        combined_low = {}
        combined_zero = []
        combined_monthly = {}
        combined_all = {}

        for item in results:
            result = item.get("result", {}) if isinstance(item, dict) else {}

            if result.get("type") == "structured":
                for key, value in _safe_dict(result.get("top_selling")).items():
                    combined_top[key] = combined_top.get(key, 0) + value

                for key, value in _safe_dict(result.get("low_selling")).items():
                    combined_low[key] = combined_low.get(key, 0) + value

                combined_zero.extend(_safe_list(result.get("zero_sales")))

                for key, value in _safe_dict(result.get("monthly_sales")).items():
                    combined_monthly[key] = combined_monthly.get(key, 0) + value

                for key, value in _safe_dict(result.get("all_products")).items():
                    combined_all[key] = combined_all.get(key, 0) + value

        combined_top = dict(sorted(combined_top.items(), key=lambda x: x[1], reverse=True)[:5])
        combined_low = dict(sorted(combined_low.items(), key=lambda x: x[1])[:5])

        total_products = len(combined_all)
        total_sales_value = sum(combined_all.values()) if combined_all else 0

        return {
            "summary": "ZIP analyzed successfully.",
            "details": {
                "top_selling": combined_top,
                "low_selling": combined_low,
                "zero_sales": list(set(combined_zero)),
                "total_products": total_products,
                "total_sales_value": round(float(total_sales_value), 2),
                "monthly_sales": combined_monthly,
                "all_products": combined_all,
                "content_preview": "",
            },
            "recommendation": {
                "buy_more": list(combined_top.keys()),
                "avoid": list(combined_low.keys()),
                "festival": recommend_festival(list(combined_top.keys())),
            },
        }

    return {"error": "Unsupported analysis type"}