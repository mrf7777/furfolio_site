from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import EmailField
from django.core.exceptions import ValidationError
from django import forms
from django.utils import timezone
from django.forms.renderers import TemplatesSetting
from .models import User, Offer, Commission, CommissionMessage


class TextSearchForm(forms.Form):
    template_name = "furfolio/form_templates/grid.html"
    text_query = forms.CharField(
        label="Search", max_length=300, required=False)


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


class UserSearchForm(TextSearchForm):
    pass


class CommissionSearchForm(TextSearchForm):
    i_am_creator = forms.BooleanField(required=False)
    i_am_buyer = forms.BooleanField(required=False)


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
        fields = ["name", "description", "cutoff_date", "thumbnail",
                  "rating", "slots", "max_review_commissions"]
        widgets = {
            "thumbnail": forms.ClearableFileInput(),
        }


class OfferFormUpdate(OfferForm):
    class Meta(OfferForm.Meta):
        model = Offer
        fields = ["name", "description",
                  "forced_closed", "cutoff_date", "thumbnail", "rating", "slots", "max_review_commissions"]


class OfferSearchForm(TextSearchForm):
    pass


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


class UpdateCommissionForm(CommissionForm):
    class Meta(CommissionForm.Meta):
        fields = ["commissioner", "offer",
                  "state", "initial_request_text", "attachment"]


class CommissionMessageForm(forms.ModelForm):
    class Meta:
        model = CommissionMessage
        fields = ["message", "attachment"]
