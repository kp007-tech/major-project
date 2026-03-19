from django.contrib import admin
from .models import ForecastResult, FuturePrediction


class FuturePredictionInline(admin.TabularInline):
    model = FuturePrediction
    extra = 0


@admin.register(ForecastResult)
class ForecastResultAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'dataset',
        'model_name',
        'mae',
        'mse',
        'rmse',
        'r2',
        'is_best',
        'created_at',
    )
    list_filter = ('model_name', 'is_best', 'created_at')
    search_fields = ('model_name',)
    inlines = [FuturePredictionInline]


@admin.register(FuturePrediction)
class FuturePredictionAdmin(admin.ModelAdmin):
    list_display = ('id', 'forecast_result', 'date', 'predicted_sales')
    list_filter = ('date',)
    search_fields = ('forecast_result__model_name',)