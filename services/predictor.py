import pandas as pd
from sklearn.linear_model import LinearRegression


def predict_future_sales(file_path, days=7):
    lower_path = str(file_path).lower()

    if lower_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    elif lower_path.endswith(".xlsx") or lower_path.endswith(".xls"):
        df = pd.read_excel(file_path)
    else:
        return {"error": "Prediction only supports CSV or Excel files"}

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    date_candidates = ["date", "order_date", "invoice_date", "sales_date"]
    sales_candidates = ["sales", "sales_amount", "amount", "revenue", "total_sales"]

    date_col = next((c for c in date_candidates if c in df.columns), None)
    sales_col = next((c for c in sales_candidates if c in df.columns), None)

    if not date_col or not sales_col:
        return {"error": "Dataset must contain date and sales columns for prediction"}

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
    df = df.dropna(subset=[date_col, sales_col]).sort_values(date_col)

    if len(df) < 2:
        return {"error": "Not enough data for prediction"}

    daily = df.groupby(date_col)[sales_col].sum().reset_index()
    daily["day_number"] = range(len(daily))

    X = daily[["day_number"]]
    y = daily[sales_col]

    model = LinearRegression()
    model.fit(X, y)

    future_day_numbers = list(range(len(daily), len(daily) + days))
    predictions = model.predict(pd.DataFrame({"day_number": future_day_numbers}))

    last_date = daily[date_col].max()
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)

    result = []
    for dt, pred in zip(future_dates, predictions):
        result.append({
            "date": dt.strftime("%Y-%m-%d"),
            "predicted_sales": round(float(max(pred, 0)), 2)
        })

    return {"predictions": result}