import pandas as pd


def predict_future(model, last_date, days=7):
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)

    future_df = pd.DataFrame({
        "day": future_dates.day,
        "month": future_dates.month,
        "year": future_dates.year,
        "day_of_week": future_dates.dayofweek,
    })

    predictions = model.predict(future_df)

    return [
        {
            "date": d.date(),
            "predicted_sales": round(float(p), 2)
        }
        for d, p in zip(future_dates, predictions)
    ]