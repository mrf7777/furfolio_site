from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .. import models
from .. import mixins
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from .. import forms
from .pagination import PageRangeContextMixin, PAGE_SIZE
from .commissions import Commissions


class OfferList(
        PageRangeContextMixin,
        mixins.GetAdultConsentMixin,
        generic.ListView):
    model = models.Offer
    template_name = "furfolio/offers/offer_list.html"
    context_object_name = "offer_list"
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        search_form = forms.OfferSearchForm(self.request.GET)
        consent_to_adult_content = self.does_user_consent_to_adult_content()
        if search_form.is_valid():
            text_query = search_form.cleaned_data["text_query"].strip()
            author = search_form.cleaned_data["author"].strip()
            sort = search_form.cleaned_data["sort"]
            closed_offers = search_form.cleaned_data["closed_offers"]
            price_min = search_form.cleaned_data["price_min"]
            price_max = search_form.cleaned_data["price_max"]

            offer_query = offer_queries.OfferSearchQuery(
                text_query=text_query,
                sort=sort,
                author=author,
                closed_offers=closed_offers,
                price_min=price_min,
                price_max=price_max,
                consent_to_adult_content=consent_to_adult_content
            )

            return offer_queries.full_text_search_offers(offer_query)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["search_form"] = forms.OfferSearchForm(self.request.GET)
        return context


class Offer(mixins.GetAdultConsentMixin,
            UserPassesTestMixin, generic.DetailView):
    model = models.Offer
    context_object_name = "offer"
    template_name = "furfolio/offers/offer_detail.html"

    def test_func(self) -> bool | None:
        match self.get_object().rating:
            case models.RATING_GENERAL:
                return True
            case models.RATING_ADULT:
                return self.does_user_consent_to_adult_content()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["should_show_create_commission_button"] = self.should_show_create_commission_button()

        offer: models.Offer = self.get_object()
        commissions_of_offer_query = commission_queries.CommissionsSearchQuery(
            offer=offer.pk
        )
        commissions_of_offer_url = Commissions.url_for_query(
            commissions_of_offer_query)
        context["see_commissions_url"] = commissions_of_offer_url

        return context

    def should_show_create_commission_button(self) -> bool:
        offer = self.get_object()
        if self.request.user.is_authenticated:
            return self.request.user.can_commission_offer(offer)
        else:
            return None


class CreateOffer(LoginRequiredMixin, generic.CreateView):
    model = models.Offer
    form_class = forms.OfferForm
    template_name = "furfolio/offers/offer_form.html"

    def get_initial(self) -> dict[str, Any]:
        initial = super().get_initial()
        initial["author"] = self.request.user
        return initial


class UpdateOffer(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = models.Offer
    form_class = forms.OfferFormUpdate
    template_name = "furfolio/offers/offer_update_form.html"

    # TODO: use the slightly more efficient version
    # https://www.django-antipatterns.com/antipattern/checking-ownership-through-the-userpassestestmixin.html
    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk


class DeleteOffer(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = models.Offer
    template_name = "furfolio/offers/offer_delete.html"
    success_url = reverse_lazy("offer_list")

    def test_func(self):
        return self.get_object().author.pk == self.request.user.pk
