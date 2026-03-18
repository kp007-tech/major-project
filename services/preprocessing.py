import pandas as pd


def read_dataset(file_path):
    lower = file_path.lower()

    if lower.endswith(".xlsx") or lower.endswith(".xls"):
        return pd.read_excel(file_path)

    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue

    raise ValueError("Unable to read file. Upload valid CSV or Excel file.")


def preprocess_data(df):
    df.columns = [str(col).strip() for col in df.columns]

    date_candidates = ["Date", "date", "DATE"]
    sales_candidates = ["Sales", "sales", "SALES", "Revenue", "revenue", "Amount", "amount"]

    date_col = next((col for col in date_candidates if col in df.columns), None)
    sales_col = next((col for col in sales_candidates if col in df.columns), None)

    if not date_col or not sales_col:
        raise ValueError("Dataset must contain a date column and a sales column.")

    df = df[[date_col, sales_col]].copy()
    df.columns = ["Date", "Sales"]

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    df = df.dropna(subset=["Date", "Sales"])
    df = df.sort_values("Date")
    df = df.drop_duplicates()

    if df.empty or len(df) < 5:
        raise ValueError("Not enough valid data. Please upload at least 5 valid rows.")

    df["day"] = df["Date"].dt.day
    df["month"] = df["Date"].dt.month
    df["year"] = df["Date"].dt.year
    df["day_of_week"] = df["Date"].dt.dayofweek

    return df