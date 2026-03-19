from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT = 42
RIGHT = PAGE_WIDTH - 42
TOP = PAGE_HEIGHT - 42
BOTTOM = 42


def build_pdf_report(dataset_title, report, prediction=None, ai_insight=None):
    """
    Generate a polished PDF report matching the premium dashboard structure.
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"{dataset_title} - Business Report")

    y = TOP

    def new_page():
        nonlocal y
        pdf.showPage()
        y = TOP

    def ensure_space(required_height):
        nonlocal y
        if y - required_height < BOTTOM:
            new_page()

    def draw_header():
        nonlocal y

        # Brand
        pdf.setFont("Helvetica-Bold", 20)
        pdf.setFillColor(colors.HexColor("#4F46E5"))
        pdf.drawString(LEFT, y, "NeuroCast AI")

        # Subtitle
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(colors.HexColor("#64748B"))
        pdf.drawRightString(RIGHT, y + 2, "Premium Business Intelligence Report")

        y -= 28

        # Title
        pdf.setFont("Helvetica-Bold", 18)
        pdf.setFillColor(colors.black)
        pdf.drawString(LEFT, y, "Business Analysis Report")

        y -= 18
        pdf.setFont("Helvetica", 11)
        pdf.setFillColor(colors.HexColor("#334155"))
        pdf.drawString(LEFT, y, f"Dataset: {dataset_title}")

        y -= 16
        pdf.setStrokeColor(colors.HexColor("#CBD5E1"))
        pdf.setLineWidth(1)
        pdf.line(LEFT, y, RIGHT, y)
        y -= 18

    def draw_footer():
        page_num = pdf.getPageNumber()
        pdf.setFont("Helvetica", 9)
        pdf.setFillColor(colors.HexColor("#94A3B8"))
        pdf.drawRightString(RIGHT, 20, f"Page {page_num}")

    def section_title(text):
        nonlocal y
        ensure_space(26)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.setFillColor(colors.HexColor("#0F172A"))
        pdf.drawString(LEFT, y, text)
        y -= 16

    def paragraph(text, font_size=10.5, color="#475569", leading=14):
        nonlocal y
        if not text:
            return

        pdf.setFont("Helvetica", font_size)
        pdf.setFillColor(colors.HexColor(color))

        words = str(text).split()
        if not words:
            y -= leading
            return

        line = ""
        max_width = RIGHT - LEFT

        for word in words:
            test_line = f"{line} {word}".strip()
            if stringWidth(test_line, "Helvetica", font_size) <= max_width:
                line = test_line
            else:
                ensure_space(leading)
                pdf.drawString(LEFT, y, line)
                y -= leading
                line = word

        if line:
            ensure_space(leading)
            pdf.drawString(LEFT, y, line)
            y -= leading

        y -= 4

    def kv_box_row(items):
        """
        items: list of tuples (label, value)
        Draws up to 2 cards per row.
        """
        nonlocal y
        if not items:
            return

        card_width = (RIGHT - LEFT - 12) / 2
        card_height = 58

        for i in range(0, len(items), 2):
            ensure_space(card_height + 8)

            row_items = items[i:i + 2]
            x = LEFT

            for label, value in row_items:
                pdf.setFillColor(colors.white)
                pdf.setStrokeColor(colors.HexColor("#E2E8F0"))
                pdf.roundRect(x, y - card_height, card_width, card_height, 10, stroke=1, fill=1)

                pdf.setFont("Helvetica", 9)
                pdf.setFillColor(colors.HexColor("#64748B"))
                pdf.drawString(x + 12, y - 18, str(label))

                pdf.setFont("Helvetica-Bold", 16)
                pdf.setFillColor(colors.HexColor("#0F172A"))
                pdf.drawString(x + 12, y - 38, str(value))

                x += card_width + 12

            y -= card_height + 12

    def bullet_list(title, items, empty_text="No data available.", value_map=None):
        nonlocal y
        section_title(title)

        if not items:
            paragraph(empty_text)
            return

        for item in items:
            ensure_space(16)

            pdf.setFont("Helvetica", 10.5)
            pdf.setFillColor(colors.HexColor("#334155"))

            if value_map and item in value_map:
                line = f"• {item}: {value_map[item]}"
            else:
                line = f"• {item}"

            wrapped_lines = wrap_text(line, "Helvetica", 10.5, RIGHT - LEFT)
            for wrapped in wrapped_lines:
                ensure_space(14)
                pdf.drawString(LEFT, y, wrapped)
                y -= 14

        y -= 4

    def wrap_text(text, font_name, font_size, max_width):
        words = str(text).split()
        if not words:
            return [""]

        lines = []
        line = ""

        for word in words:
            test_line = f"{line} {word}".strip()
            if stringWidth(test_line, font_name, font_size) <= max_width:
                line = test_line
            else:
                lines.append(line)
                line = word

        if line:
            lines.append(line)

        return lines

    def draw_predictions(predictions):
        nonlocal y
        section_title("Future Sales Prediction")

        if not predictions:
            paragraph("Prediction data is not available.")
            return

        for item in predictions:
            ensure_space(18)
            line = f"• {item.get('date', '')}: {item.get('predicted_sales', '')}"
            for wrapped in wrap_text(line, "Helvetica", 10.5, RIGHT - LEFT):
                pdf.setFont("Helvetica", 10.5)
                pdf.setFillColor(colors.HexColor("#334155"))
                pdf.drawString(LEFT, y, wrapped)
                y -= 14

        y -= 4

    def draw_ai_insight(text):
        nonlocal y
        section_title("AI Insights")

        if not text:
            paragraph("AI insight is not available right now.")
            return

        lines = str(text).splitlines()
        for line in lines:
            line = line.strip()
            if not line:
                y -= 8
                continue

            wrapped = wrap_text(line, "Helvetica", 10.5, RIGHT - LEFT)
            for w in wrapped:
                ensure_space(14)
                pdf.setFont("Helvetica", 10.5)
                pdf.setFillColor(colors.HexColor("#334155"))
                pdf.drawString(LEFT, y, w)
                y -= 14

        y -= 4

    # ----- Document content -----
    draw_header()

    summary = report.get("summary", "No summary available.")
    details = report.get("details", {}) if isinstance(report, dict) else {}
    recommendation = report.get("recommendation", {}) if isinstance(report, dict) else {}

    section_title("Executive Summary")
    paragraph(summary, font_size=11, color="#334155", leading=15)

    kv_box_row([
        ("Total Products", details.get("total_products", 0)),
        ("Total Sales Value", details.get("total_sales_value", 0)),
        ("Buy More Count", len(recommendation.get("buy_more", []))),
        ("Festival Focus", recommendation.get("festival", "N/A")),
    ])

    top_selling = details.get("top_selling", {})
    low_selling = details.get("low_selling", {})
    zero_sales = details.get("zero_sales", [])

    bullet_list(
        "Top Selling Products",
        list(top_selling.keys()),
        empty_text="No top-selling product data available.",
        value_map=top_selling,
    )

    bullet_list(
        "Low Selling Products",
        list(low_selling.keys()),
        empty_text="No low-selling product data available.",
        value_map=low_selling,
    )

    bullet_list(
        "Zero Sales Items",
        zero_sales,
        empty_text="No zero-sales items found."
    )

    buy_more = recommendation.get("buy_more", [])
    avoid = recommendation.get("avoid", [])

    bullet_list(
        "Recommended Products to Buy More",
        buy_more,
        empty_text="No buy-more recommendations available."
    )

    bullet_list(
        "Products to Avoid or Reduce",
        avoid,
        empty_text="No avoid recommendations available."
    )

    section_title("Festival Recommendation")
    paragraph(recommendation.get("festival", "No festival recommendation available."))

    if prediction and not prediction.get("error"):
        draw_predictions(prediction.get("predictions", []))
    elif prediction and prediction.get("error"):
        section_title("Future Sales Prediction")
        paragraph(prediction.get("error"))

    draw_ai_insight(ai_insight)

    draw_footer()
    pdf.save()
    buffer.seek(0)
    return buffer