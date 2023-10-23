from typing import Any
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.forms import EmailField
from django import forms
from django.forms.renderers import TemplatesSetting
from .models import User, Offer, Commission, CommissionMessage
from . import form_fields


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
        fields = UserCreationForm.Meta.fields + \
            ("email", "role", "avatar", "consent_to_adult_content")


class UpdateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["profile", "role", "email",
                  "avatar", "consent_to_adult_content"]


class UserSearchForm(TextSearchForm):
    pass


class CommissionSearchForm(forms.Form):
    template_name = "furfolio/form_templates/commission_search.html"
    sort = form_fields.SortField()
    self_managed = forms.BooleanField(required=False, initial=False)
    review = forms.BooleanField(required=False, initial=False)
    accepted = forms.BooleanField(required=False, initial=False)
    in_progress = forms.BooleanField(required=False, initial=False)
    finished = forms.BooleanField(required=False, initial=False)
    rejected = forms.BooleanField(required=False, initial=False)


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
        fields = ["author", "name", "description", "cutoff_date", "thumbnail", "max_commissions_per_user",
                  "rating", "slots", "max_review_commissions", "min_price", "max_price", "currency"]
        widgets = {
            "thumbnail": forms.ClearableFileInput(),
            "author": forms.HiddenInput(),
        }


class OfferFormUpdate(OfferForm):
    class Meta(OfferForm.Meta):
        model = Offer
        fields = ["name", "description",
                  "forced_closed", "cutoff_date", "thumbnail",
                  "rating", "slots", "max_review_commissions",
                  "max_commissions_per_user",
                  "min_price", "max_price", "currency"]


class OfferSearchForm(TextSearchForm):
    author = forms.CharField(max_length=300, required=False)
    sort = form_fields.SortField()
    closed_offers = forms.BooleanField(required=False, initial=False)
    price_min = forms.IntegerField(min_value=0, initial=0, required=False)
    price_max = forms.IntegerField(min_value=1, initial=1, required=False)

    def clean(self) -> dict[str, Any]:
        # swap the min in max if they are out of order
        price_min = self.cleaned_data["price_min"]
        price_max = self.cleaned_data["price_max"]
        if price_min is not None and price_max is not None:
            if price_min > price_max:
                self.cleaned_data["price_min"] = price_max
                self.cleaned_data["price_max"] = price_min


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
        fields = ["commission", "author", "message", "attachment"]
        widgets = {
            "commission": forms.HiddenInput(),
            "author": forms.HiddenInput(),
        }


class OfferSelectForm(forms.Form):
    template_name = "furfolio/form_templates/grid.html"

    offer = forms.ModelChoiceField(
        queryset=None, required=False, empty_label="[Show All]")

    def __init__(self, queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["offer"].queryset = queryset

    def set_queryset(self, queryset):
        self.fields["offer"].queryset = queryset
