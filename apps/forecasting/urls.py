from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('train/<int:dataset_id>/', views.train_dataset, name='train_dataset'),
]