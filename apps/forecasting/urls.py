from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    # ===== CORE PAGES =====
    path("", views.home, name="home"),

    # ===== AUTH =====
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", LogoutView.as_view(next_page="home"), name="logout"),

    # ===== DATASET FLOW =====
    path("upload/", views.upload_and_analyze, name="upload_and_analyze"),
    path("datasets/", views.dataset_list, name="dataset_list"),

    # ===== REPORT =====
    path("report/<int:dataset_id>/", views.report_view, name="report_view"),
    path(
        "report/<int:dataset_id>/download/",
        views.download_report_pdf,
        name="download_report_pdf",
    ),
]