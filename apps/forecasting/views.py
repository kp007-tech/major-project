from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme

from apps.datasets.forms import DatasetForm
from apps.datasets.models import Dataset
from .forms import CustomLoginForm, CustomRegisterForm

from services.ai_insights import generate_ai_insights
from services.file_analyzer import analyze_file
from services.pdf_exporter import build_pdf_report
from services.predictor import predict_future_sales
from services.report_generator import generate_report


def get_safe_next_url(request):
    """
    Return a safe redirect target from ?next= or POST data.
    Falls back to the home page if the URL is missing or unsafe.
    """
    next_url = request.GET.get("next") or request.POST.get("next")

    if next_url and url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url

    return resolve_url("home")


def home(request):
    return render(request, "forecasting/home.html")


def login_view(request):
    """
    Log the user in using the custom login form.
    Redirect authenticated users away from the login page.
    """
    if request.user.is_authenticated:
        return redirect("home")

    next_url = get_safe_next_url(request)
    form = CustomLoginForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Welcome back! Login successful.")
            return redirect(next_url)

        messages.error(request, "Invalid username or password.")

    context = {
        "form": form,
        "next": next_url,
    }
    return render(request, "auth/login.html", context)


def register_view(request):
    """
    Register a new user using the custom registration form.
    Automatically logs the user in after successful signup.
    """
    if request.user.is_authenticated:
        return redirect("home")

    next_url = get_safe_next_url(request)

    if request.method == "POST":
        form = CustomRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect(next_url)

        messages.error(request, "Please correct the errors below.")
    else:
        form = CustomRegisterForm()

    context = {
        "form": form,
        "next": next_url,
    }
    return render(request, "auth/register.html", context)


def _build_full_report_context(dataset, forecast_days=7):
    """
    Build the full analysis/report context for a dataset.
    This includes:
    - analyzed data
    - generated business report
    - future sales prediction
    - AI-generated insight
    """
    file_path = dataset.file.path

    analyzed_data = analyze_file(file_path)
    report = generate_report(analyzed_data)

    try:
        prediction = predict_future_sales(file_path, days=forecast_days)
    except Exception as exc:
        prediction = {"error": str(exc)}

    try:
        ai_insight = generate_ai_insights(report, prediction)
    except Exception as exc:
        ai_insight = f"AI insight is currently unavailable: {str(exc)}"

    return {
        "dataset": dataset,
        "report": report,
        "prediction": prediction,
        "ai_insight": ai_insight,
    }


@login_required
def upload_and_analyze(request):
    """
    Upload a dataset, save it for the authenticated user,
    analyze it, and render the report page.
    """
    if request.method == "POST":
        form = DatasetForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                dataset = form.save(commit=False)
                dataset.user = request.user
                dataset.save()

                context = _build_full_report_context(dataset)

                if context["report"].get("error"):
                    messages.warning(request, context["report"]["error"])
                else:
                    messages.success(request, "File uploaded and analyzed successfully.")

                return render(request, "forecasting/report.html", context)

            except Exception as exc:
                messages.error(request, f"Error processing file: {str(exc)}")
                return redirect("upload_and_analyze")

        messages.error(request, "Invalid form data. Please check your file and try again.")
    else:
        form = DatasetForm()

    return render(request, "datasets/upload.html", {"form": form})


@login_required
def dataset_list(request):
    """
    Show all datasets uploaded by the current user.
    """
    datasets = Dataset.objects.filter(user=request.user).order_by("-id")

    return render(
        request,
        "datasets/dataset_list.html",
        {
            "datasets": datasets,
        },
    )


@login_required
def report_view(request, dataset_id):
    """
    Re-open the report page for a previously uploaded dataset.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)

    try:
        context = _build_full_report_context(dataset)
        return render(request, "forecasting/report.html", context)
    except Exception as exc:
        messages.error(request, f"Unable to load report: {str(exc)}")
        return redirect("dataset_list")


@login_required
def download_report_pdf(request, dataset_id):
    """
    Generate and return the PDF version of the dataset report.
    """
    dataset = get_object_or_404(Dataset, id=dataset_id, user=request.user)

    try:
        context = _build_full_report_context(dataset)

        pdf_buffer = build_pdf_report(
            dataset_title=dataset.title,
            report=context["report"],
            prediction=context["prediction"],
            ai_insight=context["ai_insight"],
        )

        filename = f"{dataset.title}_business_report.pdf".replace(" ", "_")

        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=filename,
        )

    except Exception as exc:
        messages.error(request, f"Unable to generate PDF report: {str(exc)}")
        return redirect("report_view", dataset_id=dataset.id)