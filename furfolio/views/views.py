from typing import Any, List
from django.db.models.query import QuerySet
from django.forms.models import BaseModelForm
from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.views import generic
from django.core.paginator import Page
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from .. import models
from .. import mixins
from .. import utils
from ..forms import CommissionSearchForm, CustomUserCreationForm, OfferForm, CommissionForm, UpdateUserForm, OfferFormUpdate, OfferSearchForm, UserSearchForm, UpdateCommissionForm, CommissionMessageForm


PAGE_SIZE = 10


def get_page_range_items(page: Page) -> List[str]:
    """
    Given the page object, which you should get from the context, this
    will return a list of page items, including ellipsis, that you
    can then display in a template.
    """
    return list(page.paginator.get_elided_page_range(page.number))


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

    MAX_COMMISSIONS_PER_COLUMN = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        current_user_pk = self.request.user.pk
        review_commissions = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_REVIEW,
        ).order_by("-updated_date")
        accepted_commissions = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_ACCEPTED
        ).order_by("-updated_date")
        in_progress_commissions = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_IN_PROGRESS,
        ).order_by("-updated_date")
        closed_commissions = models.Commission.objects.filter(
            offer__author__pk=current_user_pk,
            state=models.Commission.STATE_CLOSED
        ).order_by("-updated_date")

        review_commissions_total_count = review_commissions.count()
        accepted_commissions_total_count = accepted_commissions.count()
        in_progress_commissions_total_count = in_progress_commissions.count()
        closed_commissions_total_count = closed_commissions.count()
        context["review_commissions_total_count"] = review_commissions_total_count
        context["accepted_commissions_total_count"] = accepted_commissions_total_count
        context["in_progress_commissions_total_count"] = in_progress_commissions_total_count
        context["closed_commissions_total_count"] = closed_commissions_total_count

        max_commissions_per_column = self.__class__.MAX_COMMISSIONS_PER_COLUMN
        context["review_commissions"] = review_commissions[:max_commissions_per_column]
        context["accepted_commissions"] = accepted_commissions[:max_commissions_per_column]
        context["in_progress_commissions"] = in_progress_commissions[:max_commissions_per_column]
        context["closed_commissions"] = closed_commissions[:max_commissions_per_column]

        context["review_commissions_overflow"] = review_commissions_total_count > max_commissions_per_column
        context["accepted_commissions_overflow"] = accepted_commissions_total_count > max_commissions_per_column
        context["in_progress_commissions_overflow"] = in_progress_commissions_total_count > max_commissions_per_column
        context["closed_commissions_overflow"] = closed_commissions_total_count > max_commissions_per_column

        return context


class BuyerDashboard(LoginRequiredMixin, generic.ListView):
    template_name = "furfolio/dashboards/buyer.html"
    context_object_name = "commissions"
    model = models.Commission
    paginate_by = PAGE_SIZE

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self) -> QuerySet[Any]:
        return models.Commission.objects.filter(
            commissioner=self.request.user.pk,
        ).order_by("-updated_date")


class OfferList(mixins.GetAdultConsentMixin, generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = OfferSearchForm(self.request.GET)
        consent_to_adult_content = self.does_user_consent_to_adult_content()
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            author = search_form.cleaned_data["author"].strip()
            sort = search_form.cleaned_data["sort"]
            closed_offers = search_form.cleaned_data["closed_offers"]
            return models.Offer.full_text_search_offers(text_query, author, sort, closed_offers, consent_to_adult_content)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = OfferSearchForm(self.request.GET)
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context


class Offer(mixins.GetAdultConsentMixin, UserPassesTestMixin, generic.DetailView):
    model = models.Offer
    context_object_name = "offer"
    template_name = "furfolio/offers/offer_detail.html"

    def test_func(self) -> bool | None:
        match self.get_object().rating:
            case models.Offer.RATING_GENERAL:
                return True
            case models.Offer.RATING_ADULT:
                return self.does_user_consent_to_adult_content()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["should_show_create_commission_button"] = self.should_show_create_commission_button()
        return context

    def should_show_create_commission_button(self) -> bool:
        offer = self.get_object()
        if self.request.user == offer.author:
            return True
        elif offer.is_closed():
            return False
        elif offer.has_max_review_commissions():
            return False
        else:
            return True


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CreateOffer(LoginRequiredMixin, generic.CreateView):
    model = models.Offer
    form_class = OfferForm
    template_name = "furfolio/offers/offer_form.html"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user
        return initial


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
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = UserSearchForm(self.request.GET)
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            return models.User.full_text_search_creators(text_query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = UserSearchForm(self.request.GET)
        context["page_range"] = get_page_range_items(context["page_obj"])
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

    def get_queryset(self) -> QuerySet[Any]:
        form = CommissionSearchForm(self.request.GET)
        if form.is_valid():
            return models.Commission.search_commissions(
                current_user=self.request.user,
                sort=form.cleaned_data["sort"],
                self_managed=form.cleaned_data["self_managed"],
                review=form.cleaned_data["review"],
                accepted=form.cleaned_data["accepted"],
                in_progress=form.cleaned_data["in_progress"],
                closed=form.cleaned_data["finished"],
                rejected=form.cleaned_data["rejected"],
            )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        search_form = None
        # https://stackoverflow.com/a/43096716
        if self.request.GET & CommissionSearchForm.base_fields.keys():
            search_form = CommissionSearchForm(self.request.GET)
        else:
            search_form = CommissionSearchForm()
        context["form"] = search_form
        context["page_range"] = get_page_range_items(context["page_obj"])
        return context


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
        print(redirect_url)
        print(redirect(redirect_url))
        return redirect(redirect_url)


class CommissionChat(LoginRequiredMixin, UserPassesTestMixin, generic.CreateView):
    model = models.CommissionMessage
    form_class = CommissionMessageForm
    template_name = "furfolio/commissions/chat/chat.html"

    def get_commission(self):
        return get_object_or_404(models.Commission, pk=self.kwargs["pk"])

    def get_initial(self) -> dict[str, Any]:
        commission = self.get_commission()
        initial = super().get_initial()
        initial["commission"] = commission
        initial["author"] = self.request.user
        return initial

    def test_func(self):
        object = self.get_commission()
        if object.is_self_managed():
            return False
        elif object.offer.author.pk == self.request.user.pk:
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
        context["other_user"] = utils.get_other_user_in_commission(
            self.request.user, commission)
        return context
