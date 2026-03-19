import os
from openai import OpenAI


def _safe_report_snapshot(report):
    """
    Build a compact, business-friendly summary from the report dict
    so the AI receives clean structured context instead of raw nested data.
    """
    if not isinstance(report, dict):
        return {
            "summary": "No valid report data available.",
            "top_selling": {},
            "low_selling": {},
            "zero_sales": [],
            "buy_more": [],
            "avoid": [],
            "festival": "N/A",
            "total_products": 0,
            "total_sales_value": 0,
        }

    details = report.get("details", {}) if isinstance(report.get("details"), dict) else {}
    recommendation = report.get("recommendation", {}) if isinstance(report.get("recommendation"), dict) else {}

    return {
        "summary": report.get("summary", "No summary available."),
        "top_selling": details.get("top_selling", {}),
        "low_selling": details.get("low_selling", {}),
        "zero_sales": details.get("zero_sales", []),
        "buy_more": recommendation.get("buy_more", []),
        "avoid": recommendation.get("avoid", []),
        "festival": recommendation.get("festival", "N/A"),
        "total_products": details.get("total_products", 0),
        "total_sales_value": details.get("total_sales_value", 0),
    }


def _safe_prediction_snapshot(prediction):
    """
    Normalize prediction payload for prompt building.
    """
    if not isinstance(prediction, dict):
        return {
            "error": "No valid prediction data available.",
            "predictions": []
        }

    return {
        "error": prediction.get("error", ""),
        "predictions": prediction.get("predictions", []),
    }


def generate_ai_insights(report, prediction=None):
    """
    Generate premium business recommendations for the dashboard and PDF report.
    Returns plain text with strong business tone and actionable guidance.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "AI insight is unavailable because OPENAI_API_KEY is not configured.\n\n"
            "Set your API key in the environment to enable advanced business recommendations."
        )

    client = OpenAI(api_key=api_key)

    report_data = _safe_report_snapshot(report)
    prediction_data = _safe_prediction_snapshot(prediction)

    prompt = f"""
You are an expert retail growth strategist and sales intelligence consultant.

Create a premium, practical business insight report for a dashboard user.

Use the data below and respond in a polished business style.
Keep it clear, actionable, and concise.
Do not repeat raw JSON.
Do not mention that you are an AI.

You must include these sections exactly:

1. Executive Insight
2. What to Stock More
3. What to Reduce or Avoid
4. Sales Trend Observation
5. Festival / Seasonal Preparation
6. Recommended Next Action

Rules:
- Use short business paragraphs or bullet-style lines.
- Be specific when referencing top-selling or weak products.
- If prediction data exists, mention future demand direction.
- If data is limited, say so professionally and still give useful advice.
- Focus on retail/business value, not technical explanation.

Report Summary:
{report_data['summary']}

Total Products:
{report_data['total_products']}

Total Sales Value:
{report_data['total_sales_value']}

Top Selling:
{report_data['top_selling']}

Low Selling:
{report_data['low_selling']}

Zero Sales:
{report_data['zero_sales']}

Recommended Buy More:
{report_data['buy_more']}

Recommended Avoid:
{report_data['avoid']}

Festival Recommendation:
{report_data['festival']}

Prediction Error:
{prediction_data['error']}

Predictions:
{prediction_data['predictions']}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a sharp business analyst who writes premium dashboard insights "
                        "for retail, sales, and inventory decision-making."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.45,
        )

        content = response.choices[0].message.content
        return content.strip() if content else "AI insight could not be generated."

    except Exception as e:
        return f"AI insight generation failed: {str(e)}"