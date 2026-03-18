from django import forms
from .models import SalesDataset


class SalesDatasetForm(forms.ModelForm):
    class Meta:
        model = SalesDataset
        fields = ['title', 'csv_file']

    def clean_csv_file(self):
        file = self.cleaned_data['csv_file']
        allowed_extensions = ['.csv', '.xlsx', '.xls']

        if not any(file.name.lower().endswith(ext) for ext in allowed_extensions):
            raise forms.ValidationError("Only CSV or Excel files are allowed.")

        return file