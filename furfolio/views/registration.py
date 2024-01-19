
from typing import Any
from django.utils.http import urlencode
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseServerError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.contrib import auth
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from honeypot.decorators import check_honeypot
import django_email_verification
from .. import forms
from .. import models

# decorate the 'post' method of this class to check for honeypot


@method_decorator(check_honeypot, name="post")
class SignUp(generic.CreateView):
    form_class = forms.CustomUserCreationForm
    template_name = "registration/signup.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        # verify email
        # from https://github.com/LeoneBacciu/django-email-verification?tab=readme-ov-file#email-sending
        response = super().form_valid(form)
        user = self.object
        user.is_active = False
        user.full_clean()
        user.save()
        django_email_verification.send_email(user)

        # sign in the new user

        # username = self.request.POST["username"]
        # password = self.request.POST["password1"]
        # user = auth.authenticate(username=username, password=password)
        # if user is not None:
        #     auth.login(self.request, user)
        # else:
        #     return HttpResponseServerError()

        return response
    
    def get_success_url(self) -> str:
        user = self.object
        encoded_email = urlencode({"email": user.email})
        root_url = reverse_lazy("please_verify_email")
        return f"{root_url}?{encoded_email}"


class PleaseVerifyEmail(generic.TemplateView):
    template_name = "furfolio/verify_email/please_verify_email.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["email"] = self.request.GET.get("email")
        return context


class AfterSignUp(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/pages/after_sign_up.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["show_creator_next_steps"] = self.request.user.role == models.User.ROLE_CREATOR
        context["show_buyer_next_steps"] = self.request.user.role == models.User.ROLE_BUYER
        return context
