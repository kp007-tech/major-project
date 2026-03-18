import os
import pandas as pd

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.datasets.models import Dataset
from apps.datasets.forms import DatasetForm
from services.preprocessing import load_dataset_file, preprocess_data


def home(request):
    return render(request, 'forecasting/home.html')


@login_required
def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.save()

            messages.success(request, "Dataset uploaded successfully.")
            return redirect('train_dataset', dataset_id=dataset.id)
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = DatasetForm()

    return render(request, 'datasets/upload.html', {'form': form})


@login_required
def train_dataset(request, dataset_id):
    dataset = get_object_or_404(Dataset, id=dataset_id)

    try:
        df = load_dataset_file(dataset.file.path)
        df = preprocess_data(df)

        print("Processed Data:")
        print(df.head())

        return render(
            request,
            'forecasting/train_result.html',
            {
                'dataset': dataset,
                'columns': df.columns.tolist(),
                'rows': df.head(10).to_dict(orient='records'),
            }
        )

    except Exception as e:
        messages.error(request, f"Training failed: {str(e)}")
        return redirect('upload_dataset')