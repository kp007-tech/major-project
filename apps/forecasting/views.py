import json
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.datasets.models import Dataset
from .models import ForecastResult, FuturePrediction
from services.preprocessing import read_dataset, preprocess_data
from services.model_training import train_all_models, get_best_model
from services.prediction import predict_future




def home(request):
    return render(request, 'forecasting/home.html')


@login_required
def train_dataset(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)

    # Clear old results for retraining
    ForecastResult.objects.filter(dataset=dataset).delete()

    df = read_dataset(dataset.file.path)
    df = preprocess_data(df)

    X = df[['day', 'month', 'year', 'day_of_week']]
    y = df['Sales']

    trained_results = train_all_models(X, y)
    best_model_name, best_model_info = get_best_model(trained_results)

    saved_results = []

    for model_name, info in trained_results.items():
        result = ForecastResult.objects.create(
            dataset=dataset,
            model_name=model_name,
            mae=round(info['mae'], 2),
            mse=round(info['mse'], 2),
            rmse=round(info['rmse'], 2),
            r2=round(info['r2'], 2),
            is_best=(model_name == best_model_name)
        )
        saved_results.append(result)

    future_data = predict_future(
        best_model_info['model'],
        df['Date'].max(),
        days=7
    )

    best_result = ForecastResult.objects.get(dataset=dataset, is_best=True)

    for row in future_data:
        FuturePrediction.objects.create(
            forecast_result=best_result,
            date=row['date'],
            predicted_sales=row['predicted_sales']
        )

    actual_dates = df['Date'].dt.strftime('%Y-%m-%d').tolist()
    actual_sales = df['Sales'].tolist()

    future_dates = [str(item['date']) for item in future_data]
    future_sales = [item['predicted_sales'] for item in future_data]

    context = {
        'dataset': dataset,
        'results': saved_results,
        'best_result': best_result,
        'future_predictions': best_result.future_predictions.all(),
        'actual_dates_json': json.dumps(actual_dates),
        'actual_sales_json': json.dumps(actual_sales),
        'future_dates_json': json.dumps(future_dates),
        'future_sales_json': json.dumps(future_sales),
    }
    return render(request, 'forecasting/train_result.html', context)