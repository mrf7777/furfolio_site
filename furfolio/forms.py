from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone
from django.forms.renderers import TemplatesSetting
from .models import User, Offer, Commission


class CustomFormRenderer(TemplatesSetting):
    form_template_name = "furfolio/form_template.html"

# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#custom-users-and-the-built-in-auth-forms


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})
        self.fields["avatar"].widget.attrs.update({"class": "form-control"})
        self.fields["role"].widget.attrs.update({"class": "form-control"})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "role", "avatar")


class UpdateUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].widget.attrs.update({"class": "form-control"})
        self.fields["email"].widget.attrs.update({"class": "form-control"})
        self.fields["avatar"].widget.attrs.update({"class": "form-control"})
    
    class Meta:
        model = User
        fields = ["role", "email", "avatar"]


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password"].widget.attrs.update({"class": "form-control"})


class OfferForm(forms.ModelForm):
    cutoff_date = forms.SplitDateTimeField(
        help_text="When you offer is no longer accepting commissions.",
        label="Cutoff Time",
        widget=forms.SplitDateTimeWidget(
            date_attrs={"type": "date", "class": "form-control"}, time_attrs={"type": "time", "class": "form-control mt-1"}
        ),
    )

    class Meta:
        model = Offer
        fields = ["name", "cutoff_date", "thumbnail"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class OfferFormUpdate(OfferForm):
    class Meta(OfferForm.Meta):
        model = Offer
        fields = ["name", "forced_closed", "cutoff_date", "thumbnail"]
        widgets = {
            **OfferForm.Meta.widgets,
            "forced_closed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ["commissioner", "offer", "initial_request_text"]
        widgets = {
            "commissioner": forms.HiddenInput(),
            "offer": forms.HiddenInput(),
            "initial_request_text": forms.Textarea(attrs={"class": "form-control"})
        }