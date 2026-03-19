from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User


INPUT_CLASS = "input"
SELECT_CLASS = "input"


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Enter your username",
                "autocomplete": "username",
                "id": "id_username",
            }
        ),
    )

    password = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
                "id": "id_password",
            }
        ),
    )


class CustomRegisterForm(UserCreationForm):
    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Choose a username",
                "autocomplete": "username",
                "id": "id_username",
            }
        ),
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )

    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Enter your email address",
                "autocomplete": "email",
                "id": "id_email",
            }
        ),
    )

    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Create a strong password",
                "autocomplete": "new-password",
                "id": "id_password1",
            }
        ),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Re-enter your password",
                "autocomplete": "new-password",
                "id": "id_password2",
            }
        ),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ForecastSettingsForm(forms.Form):
    FORECAST_MODEL_CHOICES = [
        ("linear_regression", "Linear Regression"),
        ("random_forest", "Random Forest"),
        ("xgboost", "XGBoost"),
    ]

    forecast_days = forms.IntegerField(
        label="Forecast Days",
        min_value=1,
        max_value=365,
        initial=30,
        widget=forms.NumberInput(
            attrs={
                "class": INPUT_CLASS,
                "placeholder": "Enter number of days to forecast",
                "id": "id_forecast_days",
                "min": 1,
                "max": 365,
            }
        ),
        help_text="Choose how many future days you want to predict.",
    )

    model_name = forms.ChoiceField(
        label="Forecast Model",
        choices=FORECAST_MODEL_CHOICES,
        initial="linear_regression",
        widget=forms.Select(
            attrs={
                "class": SELECT_CLASS,
                "id": "id_model_name",
            }
        ),
        help_text="Select the prediction model to use for forecasting.",
    )

    def clean_forecast_days(self):
        days = self.cleaned_data.get("forecast_days")
        if days is None:
            raise forms.ValidationError("Please enter the number of forecast days.")
        if days < 1 or days > 365:
            raise forms.ValidationError("Forecast days must be between 1 and 365.")
        return days