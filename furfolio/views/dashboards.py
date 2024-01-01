from typing import Any
from django.db.models.query import QuerySet
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .. import models
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from .. import forms
from .commissions import Commissions
from .pagination import PageRangeContextMixin, PAGE_SIZE


class DashboardRedirector(LoginRequiredMixin, generic.RedirectView):
    def get_redirect_url(self, *args: Any, **kwargs: Any) -> str | None:
        if self.request.user.role == models.User.ROLE_BUYER:
            return reverse("buyer_dashboard")
        elif self.request.user.role == models.User.ROLE_CREATOR:
            return reverse("creator_dashboard")


class CreatorDashboard(LoginRequiredMixin, generic.FormView):
    template_name = "furfolio/dashboards/creator.html"
    form_class = forms.OfferSelectForm

    MAX_COMMISSIONS_PER_COLUMN = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        relevant_offers_to_show_on_board = offer_queries.get_relevant_offers_for_user(
            self.request.user)
        offer_form = forms.OfferSelectForm(
            queryset=relevant_offers_to_show_on_board, data=self.request.GET)
        offer_form.full_clean()
        context["offer_select_form"] = offer_form

        selected_offer = offer_form.cleaned_data.get("offer")
        commissions = commission_queries.get_commissions_for_user_as_offer_author(
            self.request.user,
            [
                models.Commission.STATE_REVIEW,
                models.Commission.STATE_ACCEPTED,
                models.Commission.STATE_IN_PROGRESS,
            ],
            selected_offer,
        )

        review_commissions = commissions[models.Commission.STATE_REVIEW]
        accepted_commissions = commissions[models.Commission.STATE_ACCEPTED]
        in_progress_commissions = commissions[models.Commission.STATE_IN_PROGRESS]

        review_commissions_total_count = review_commissions.count()
        accepted_commissions_total_count = accepted_commissions.count()
        in_progress_commissions_total_count = in_progress_commissions.count()
        context["review_commissions_total_count"] = review_commissions_total_count
        context["accepted_commissions_total_count"] = accepted_commissions_total_count
        context["in_progress_commissions_total_count"] = in_progress_commissions_total_count

        max_commissions_per_column = self.__class__.MAX_COMMISSIONS_PER_COLUMN
        context["review_commissions"] = review_commissions[:max_commissions_per_column]
        context["accepted_commissions"] = accepted_commissions[:max_commissions_per_column]
        context["in_progress_commissions"] = in_progress_commissions[:max_commissions_per_column]

        context["review_commissions_overflow"] = review_commissions_total_count > max_commissions_per_column
        context["accepted_commissions_overflow"] = accepted_commissions_total_count > max_commissions_per_column
        context["in_progress_commissions_overflow"] = in_progress_commissions_total_count > max_commissions_per_column

        # construct urls to commission searches for each column so that the
        # user can "see all"
        review_commissions_query = commission_queries.CommissionsSearchQuery(
            review=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        review_commissions_query_url = Commissions.url_for_query(
            review_commissions_query)
        context["see_review_commissions_url"] = review_commissions_query_url

        accepted_commissions_query = commission_queries.CommissionsSearchQuery(
            accepted=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        accepted_commissions_query_url = Commissions.url_for_query(
            accepted_commissions_query)
        context["see_accepted_commissions_url"] = accepted_commissions_query_url

        in_progress_commissions_query = commission_queries.CommissionsSearchQuery(
            in_progress=True,
            offer=selected_offer.pk if selected_offer else None,
        )
        in_progress_commissions_query_url = Commissions.url_for_query(
            in_progress_commissions_query)
        context["see_in_progress_commissions_url"] = in_progress_commissions_query_url

        return context


class BuyerDashboard(
        PageRangeContextMixin,
        LoginRequiredMixin,
        generic.ListView):
    template_name = "furfolio/dashboards/buyer.html"
    context_object_name = "commissions"
    model = models.Commission
    paginate_by = PAGE_SIZE

    def get_queryset(self) -> QuerySet[Any]:
        return commission_queries.get_commissions_for_user_as_commissioner(
            self.request.user)
