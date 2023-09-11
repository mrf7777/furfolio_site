from django.contrib.auth.forms import UserCreationForm
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone
from django.forms.renderers import TemplatesSetting
from .models import User, Offer


class CustomFormRenderer(TemplatesSetting):
    form_template_name = "form_template.html"

# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#custom-users-and-the-built-in-auth-forms


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ["name", "cutoff_date"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "cutoff_date": forms.TextInput(attrs={"type": "datetime-local", "class": "form-control"})
        }

    def clean_cutoff_date(self):
        cutoff_date = self.cleaned_data["cutoff_date"]
        if cutoff_date <= timezone.now():
            raise ValidationError("Offer cutoff date cannot be in the past.")
        return cutoff_date
