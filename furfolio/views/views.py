from typing import Any
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from .. import models
from ..forms import CustomUserCreationForm, OfferForm, CommissionForm, UpdateUserForm, OfferFormUpdate, OfferSearchForm, UserSearchForm, UpdateCommissionForm, CommissionMessageForm


PAGE_SIZE = 5


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
        current_user_pk = self.request.user.pk
        context["review_commissions"] = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_REVIEW,
        ).order_by("-updated_date")
        context["accepted_commissions"] = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_ACCEPTED
        ).order_by("-updated_date")
        context["in_progress_commissions"] = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_IN_PROGRESS,
        ).order_by("-updated_date")
        context["closed_commissions"] = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_CLOSED
        ).order_by("-updated_date")
        return context


class BuyerDashboard(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/dashboards/buyer.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["commissions_as_commissioner"] = models.Commission.objects.filter(
            commissioner=self.request.user.pk,
        )
        return context


class OfferList(generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = OfferSearchForm(self.request.GET)
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            # Search something if text query is provided. Otherwise, use most recent.
            if text_query:
                return models.Offer.full_text_search_offers(text_query)
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


class UserOffers(generic.ListView):
    model = models.Offer
    context_object_name = "offers"
    template_name = "furfolio/offers/user_offer_list.html"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        username = self.kwargs["username"]
        return models.Offer.objects.filter(author__username=username)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["user"] = get_object_or_404(
            models.User, username=self.kwargs["username"])
        return context


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
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = UserSearchForm(self.request.GET)
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            # search something if text query is provided
            if text_query:
                return models.User.full_text_search_creators(text_query)
            else:
                return models.User.get_creators().order_by("-date_joined")

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
        initial["offer"] = self.kwargs["offer_pk"]
        initial["commissioner"] = self.request.user.pk
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["offer"] = get_object_or_404(
            models.Offer, pk=self.kwargs["offer_pk"])
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


class Commissions(LoginRequiredMixin, generic.ListView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_list.html"
    context_object_name = "commissions"
    paginate_by = PAGE_SIZE


class UpdateCommission(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Commission
    template_name = "furfolio/commissions/commission_update.html"
    form_class = UpdateCommissionForm
    context_object_name = "commission"

    # only let the offer author update the commission
    def test_func(self):
        return self.get_object().offer.author.pk == self.request.user.pk


class UpdateCommissionStatus(LoginRequiredMixin, generic.View):
    def post(self, request, pk):
        commission = get_object_or_404(models.Commission, pk=pk)
        # ensure that offer author only has permission to update commission state
        user = self.request.user
        if user.pk != commission.offer.author.pk:
            raise PermissionDenied(
                "You do not have the permission to change the state of this commission."
            )

        redirect_url = request.GET["next"]
        commission.state = request.POST["state"]
        commission.save()
        return redirect(redirect_url)


class CommissionChat(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = models.CommissionMessage
    form_class = CommissionMessageForm
    template_name = "furfolio/commissions/chat/chat.html"

    def get_commission(self):
        return get_object_or_404(models.Commission, pk=self.kwargs["pk"])

    def form_valid(self, form: BaseModelForm) -> HttpResponse:
        commission = self.get_commission()
        form.instance.commission = commission
        form.instance.author = self.request.user
        return super(CommissionChat, self).form_valid(form)

    def test_func(self):
        object = self.get_commission()
        if object.offer.author.pk == self.request.user.pk:
            return True
        elif object.commissioner.pk == self.request.user.pk:
            return True
        else:
            return False

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        commission = self.get_commission()
        context["commission_messages"] = models.CommissionMessage.objects.filter(
            commission__pk=commission.pk
        ).order_by("created_date")
        return context
