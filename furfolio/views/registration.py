
from django.forms.models import BaseModelForm
from django.http import HttpResponse, HttpResponseServerError
from django.views import generic
from django.contrib import auth
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from honeypot.decorators import check_honeypot
from .. import forms

# decorate the 'post' method of this class to check for honeypot


@method_decorator(check_honeypot, name="post")
class SignUp(generic.CreateView):
    form_class = forms.CustomUserCreationForm
    success_url = reverse_lazy("after_sign_up")
    template_name = "registration/signup.html"

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        response = super().form_valid(form)
        # sign in the new user
        # TODO: consider testing via LiveServerTestCase class
        username = self.request.POST["username"]
        password = self.request.POST["password1"]
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(self.request, user)
        else:
            return HttpResponseServerError()
        return response


class AfterSignUp(generic.TemplateView):
    template_name = "furfolio/pages/after_sign_up.html"