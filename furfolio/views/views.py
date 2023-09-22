from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .. import models
from ..forms import CustomUserCreationForm, OfferForm


class Home(generic.TemplateView):
    template_name = "furfolio/home.html"


class Dashboard(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/dashboard.html"


class OfferList(generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"

    def get_queryset(self) -> QuerySet[Any]:
        return models.Offer.objects.all().order_by("-created_date")


class Offer(generic.DetailView):
    model = models.Offer
    context_object_name = "offer"
    template_name = "furfolio/offers/offer_detail.html"


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CreateOffer(LoginRequiredMixin, generic.CreateView):
    model = models.Offer
    form_class = OfferForm
    template_name = "furfolio/offers/offer_form.html"

    # https://koenwoortman.com/python-django-set-current-user-create-view/
    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        form.instance.author_id = self.request.user.id
        return super().form_valid(form)


class UpdateOffer(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Offer
    form_class = OfferForm
    template_name = "furfolio/offers/offer_update_form.html"

    # TODO: use the slightly more efficient version
    # https://www.django-antipatterns.com/antipattern/checking-ownership-through-the-userpassestestmixin.html
    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk


class DeleteOffer(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = models.Offer
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "furfolio/offers/offer_delete.html"
    success_url = reverse_lazy("offer_list")

    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk


class User(generic.DetailView):
    model = models.User
    slug_field = "username"
    slug_url_kwarg = "username"
    context_object_name = "user"
    template_name = "furfolio/users/user_detail.html"


class UserList(generic.ListView):
    model = models.User
    context_object_name = "users"
    template_name = "furfolio/users/user_list.html"