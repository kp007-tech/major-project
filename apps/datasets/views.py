from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import DatasetForm
from .models import Dataset


@login_required
def upload_dataset(request):
    if request.method == 'POST':
        form = DatasetForm(request.POST, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.user = request.user
            dataset.save()
            return redirect('train_dataset', dataset_id=dataset.id)
    else:
        form = DatasetForm()

    return render(request, 'datasets/upload.html', {'form': form})


@login_required
def dataset_list(request):
    datasets = Dataset.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'datasets/dataset_list.html', {'datasets': datasets})