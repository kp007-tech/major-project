import os
import zipfile
import shutil
import tempfile
import pandas as pd

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


def read_csv_with_fallback(file_path):
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin1", "iso-8859-1"]
    last_error = None

    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except UnicodeDecodeError as e:
            last_error = e
        except Exception as e:
            last_error = e

    raise ValueError(f"Could not read CSV file. Last error: {last_error}")


def analyze_file(file_path):
    file_path = str(file_path)
    lower_path = file_path.lower()

    if lower_path.endswith(".csv"):
        df = read_csv_with_fallback(file_path)
        return analyze_dataframe(df)

    elif lower_path.endswith(".xlsx") or lower_path.endswith(".xls"):
        df = pd.read_excel(file_path)
        return analyze_dataframe(df)

    elif lower_path.endswith(".pdf"):
        return analyze_pdf(file_path)

    elif lower_path.endswith(".zip"):
        return analyze_zip(file_path)

    return {"error": "Unsupported file type"}


def analyze_dataframe(df):
    if df is None or df.empty:
        return {"error": "Uploaded file is empty or contains no usable rows"}

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace("-", "_", regex=False)
    )

    product_candidates = ["product", "product_name", "item", "item_name", "name"]
    sales_candidates = ["sales", "sales_amount", "amount", "revenue", "total_sales"]
    qty_candidates = ["qty", "quantity", "sold_quantity", "units"]
    date_candidates = ["date", "order_date", "invoice_date", "sales_date"]

    product_col = next((col for col in product_candidates if col in df.columns), None)
    sales_col = next((col for col in sales_candidates if col in df.columns), None)
    qty_col = next((col for col in qty_candidates if col in df.columns), None)
    date_col = next((col for col in date_candidates if col in df.columns), None)

    if not product_col:
        return {"error": f"No product column found. Available columns: {df.columns.tolist()}"}

    metric_col = sales_col or qty_col
    if not metric_col:
        return {"error": f"No sales or quantity column found. Available columns: {df.columns.tolist()}"}

    df = df.copy()
    df[product_col] = df[product_col].astype(str).str.strip()
    df[metric_col] = pd.to_numeric(df[metric_col], errors="coerce").fillna(0)

    grouped = df.groupby(product_col)[metric_col].sum().sort_values(ascending=False)

    top_selling = grouped.head(5).to_dict()
    low_selling = grouped.tail(5).to_dict()
    zero_sales = grouped[grouped <= 0].index.tolist()
    all_products = grouped.to_dict()

    monthly_sales = {}
    if date_col:
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        temp = df.dropna(subset=[date_col]).copy()
        if not temp.empty:
            temp["month"] = temp[date_col].dt.to_period("M").astype(str)
            monthly_sales = temp.groupby("month")[metric_col].sum().sort_index().to_dict()

    return {
        "type": "structured",
        "total_products": int(len(grouped)),
        "top_selling": top_selling,
        "low_selling": low_selling,
        "zero_sales": zero_sales,
        "all_products": all_products,
        "monthly_sales": monthly_sales,
    }


def analyze_pdf(file_path):
    if pdfplumber is None:
        return {"error": "pdfplumber is not installed. Run: pip install pdfplumber"}

    extracted_text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text += (page.extract_text() or "") + "\n"
    except Exception as e:
        return {"error": f"PDF analysis failed: {str(e)}"}

    return {
        "type": "text",
        "content": extracted_text[:3000],
    }


def analyze_zip(file_path):
    temp_dir = tempfile.mkdtemp(prefix="zip_analyze_")
    frames = []

    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        for root, _, files in os.walk(temp_dir):
            for filename in files:
                full_path = os.path.join(root, filename)
                lower_name = filename.lower()

                try:
                    if lower_name.endswith(".csv"):
                        frames.append(read_csv_with_fallback(full_path))
                    elif lower_name.endswith(".xlsx") or lower_name.endswith(".xls"):
                        frames.append(pd.read_excel(full_path))
                except Exception:
                    continue

        if not frames:
            return {"error": "No usable CSV or Excel files found inside ZIP"}

        combined = pd.concat(frames, ignore_index=True)
        return analyze_dataframe(combined)

    except Exception as e:
        return {"error": f"ZIP extraction failed: {str(e)}"}

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)