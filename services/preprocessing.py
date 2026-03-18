import pandas as pd


def load_dataset_file(file_path):
    """
    Load dataset from CSV or Excel file.
    """
    file_path = str(file_path).lower()

    if file_path.endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        return pd.read_excel(file_path)
    else:
        raise ValueError("Unsupported file format. Please upload CSV or Excel file.")


def preprocess_data(df):
    """
    Preprocess dataset and make sure it has usable date and sales columns.
    """

    # Normalize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    print("Detected dataset columns:", df.columns.tolist())

    # Possible column names for date
    date_candidates = [
        'date',
        'order_date',
        'invoice_date',
        'sales_date',
        'day',
        'timestamp',
        'datetime'
    ]

    # Possible column names for sales
    sales_candidates = [
        'sales',
        'sale',
        'revenue',
        'amount',
        'total_sales',
        'income',
        'turnover',
        'profit'
    ]

    date_col = None
    sales_col = None

    # Find date column
    for col in df.columns:
        if col in date_candidates:
            date_col = col
            break

    # Find sales column
    for col in df.columns:
        if col in sales_candidates:
            sales_col = col
            break

    if not date_col or not sales_col:
        raise ValueError(
            f"Dataset must contain a valid date column and sales column. "
            f"Found columns: {df.columns.tolist()}"
        )

    # Rename to standard names
    df = df.rename(columns={
        date_col: 'date',
        sales_col: 'sales'
    })

    # Convert types
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['sales'] = pd.to_numeric(df['sales'], errors='coerce')

    # Remove invalid rows
    df = df.dropna(subset=['date', 'sales'])

    if df.empty:
        raise ValueError("Dataset has no valid rows after cleaning date and sales columns.")

    # Sort by date
    df = df.sort_values('date')

    # Reset index
    df = df.reset_index(drop=True)

    return df