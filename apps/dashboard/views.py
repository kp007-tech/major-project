import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.datasets.models import Dataset
from apps.forecasting.models import ForecastResult


@login_required
def dashboard_view(request):
    datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
    best_results = ForecastResult.objects.filter(dataset__user=request.user, is_best=True).select_related('dataset')

    total_datasets = datasets.count()
    total_models = ForecastResult.objects.filter(dataset__user=request.user).count()
    best_model_count = best_results.count()

    chart_labels = [result.dataset.title for result in best_results]
    chart_scores = [result.r2 for result in best_results]

    context = {
        'datasets': datasets,
        'best_results': best_results,
        'total_datasets': total_datasets,
        'total_models': total_models,
        'best_model_count': best_model_count,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_scores_json': json.dumps(chart_scores),
    }
    return render(request, 'dashboard/index.html', context)