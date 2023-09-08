from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django import forms
from .models import User, Offer

# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#custom-users-and-the-built-in-auth-forms
class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)
        
class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["name", "cutoff_date"]
        widgets = {
            "cutoff_date": forms.TextInput(attrs={"type": "datetime-local"})
        }