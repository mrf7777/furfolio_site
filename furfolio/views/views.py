from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import render
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.urls import reverse_lazy, reverse
from .. import models
from ..forms import CustomUserCreationForm, OfferForm, CommissionForm, UpdateUserForm, OfferFormUpdate, OfferSearchForm, UserSearchForm


class Home(generic.TemplateView):
    template_name = "furfolio/home.html"


class DashboardRedirector(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str | None:
        if self.request.user.role == models.User.ROLE_BUYER:
            return reverse("buyer_dashboard")
        elif self.request.user.role == models.User.ROLE_CREATOR:
            return reverse("creator_dashboard")


class CreatorDashboard(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/dashboards/creator.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["commissions_in_review"] = models.Commission.objects.filter(
            offer__author=self.request.user.pk,
            state=models.Commission.STATE_REVIEW,
        )
        return context


class BuyerDashboard(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/dashboards/buyer.html"


class OfferList(generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        # Search something if text query is provided. Otherwise, use most recent.
        if "text_query" in self.request.GET and self.request.GET["text_query"].strip() != "":
            search_vector = SearchVector("name", weight="A")
            search_query = SearchQuery(self.request.GET["text_query"])
            search_rank = SearchRank(search_vector, search_query)
            return models.Offer.objects.annotate(rank=search_rank).filter(rank__gte=0.2).order_by("-rank")
        else:
            return models.Offer.objects.all().order_by("-created_date")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = OfferSearchForm(self.request.GET)
        return context


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
    form_class = OfferFormUpdate
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


class UpdateUser(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.User
    form_class = CustomUserCreationForm
    template_name = "furfolio/users/user_update.html"
    context_object_name = "user"
    slug_field = "username"
    slug_url_kwarg = "username"
    form_class = UpdateUserForm

    def test_func(self):
        return self.get_object().pk == self.request.user.pk


class UserList(generic.ListView):
    model = models.User
    context_object_name = "users"
    template_name = "furfolio/users/user_list.html"
    paginate_by = 5

    def get_queryset(self) -> QuerySet[Any]:
        # search something if text query is provided
        if "text_query" in self.request.GET:
            search_vector = SearchVector("username")
            search_query = SearchQuery(self.request.GET["text_query"])
            search_rank = SearchRank(search_vector, search_query)
            return models.User.objects.filter(role=models.User.ROLE_CREATOR).annotate(rank=search_rank).order_by("-rank")
        else:
            return models.User.objects.filter(role=models.User.ROLE_CREATOR).order_by("-date_joined")

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET)
        return context


class CreateCommission(LoginRequiredMixin, generic.CreateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_create.html"
    form_class = CommissionForm

    # prefill offer and commissioner for the commission since these are hidden fields
    def get_initial(self):
        initial = super().get_initial()
        initial["offer"] = self.request.GET["offer"]
        initial["commissioner"] = self.request.GET["commissioner"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = models.Offer.objects.filter(
            pk=self.request.GET["offer"])[0]
        return context


class Commission(LoginRequiredMixin, UserPassesTestMixin, generic.DetailView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_detail.html"
    context_object_name = "commission"

    def test_func(self):
        object = self.get_object()
        if object.offer.author.pk == self.request.user.pk:
            return True
        elif object.commissioner.pk == self.request.user.pk:
            return True
        else:
            return False


class UpdateCommission(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_update.html"
    form_class = CommissionForm
    context_object_name = "commission"

    # only let the offer author update the commission
    def test_func(self):
        return self.get_object().offer.author.pk == self.request.user.pk
