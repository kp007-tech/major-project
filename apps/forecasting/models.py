from django.db import models
from apps.datasets.models import Dataset


class ForecastResult(models.Model):
    dataset = models.ForeignKey(
        Dataset,
        on_delete=models.CASCADE,
        related_name='forecast_results'
    )
    model_name = models.CharField(max_length=100)
    mae = models.FloatField(default=0)
    mse = models.FloatField(default=0)
    rmse = models.FloatField(default=0)
    r2 = models.FloatField(default=0)
    is_best = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        dataset_label = getattr(self.dataset, 'title', None) or getattr(self.dataset, 'name', None) or f'Dataset {self.dataset_id}'
        return f"{dataset_label} - {self.model_name}"


class FuturePrediction(models.Model):
    forecast_result = models.ForeignKey(
        ForecastResult,
        on_delete=models.CASCADE,
        related_name='future_predictions'
    )
    date = models.DateField()
    predicted_sales = models.FloatField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.forecast_result.model_name} - {self.date}"