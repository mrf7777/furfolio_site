from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone
from django.forms.renderers import TemplatesSetting
from .models import User, Offer, Commission


class CustomFormRenderer(TemplatesSetting):
    form_template_name = "furfolio/form_templates/default.html"

# https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#custom-users-and-the-built-in-auth-forms


class CustomUserCreationForm(UserCreationForm):
    email = EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ("email", "role", "avatar")


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["role", "email", "avatar"]


class LoginForm(AuthenticationForm):
    pass


class OfferForm(forms.ModelForm):
    cutoff_date = forms.SplitDateTimeField(
        help_text="When your offer is no longer accepting commissions.",
        label="Cutoff Time",
        widget=forms.SplitDateTimeWidget(),
    )

    class Meta:
        model = Offer
        fields = ["name", "description", "cutoff_date", "thumbnail"]
        widgets = {
            "thumbnail": forms.ClearableFileInput(),
        }


class OfferFormUpdate(OfferForm):
    class Meta(OfferForm.Meta):
        model = Offer
        fields = ["name", "description",
                  "forced_closed", "cutoff_date", "thumbnail"]


class OfferSearchForm(forms.Form):
    template_name = "furfolio/form_templates/grid.html"
    text_query = forms.CharField(
        label="Text Search", max_length=300, required=False)


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ["commissioner", "offer",
                  "initial_request_text", "attachment"]
        widgets = {
            "commissioner": forms.HiddenInput(),
            "offer": forms.HiddenInput(),
            "initial_request_text": forms.Textarea(),
            "attachment": forms.ClearableFileInput(),
        }
