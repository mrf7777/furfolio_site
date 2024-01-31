from typing import Any
from django.db.models.query import QuerySet
from django.http import QueryDict
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from .. import models
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from .. import forms
from .commissions import Commissions
from .pagination import PageRangeContextMixin, PAGE_SIZE


def make_context_for_dashboard(
        context: dict[str, Any],
        current_user,
        max_commissions_per_column: int,
        get_params: QueryDict,
) -> dict[str, Any]:
    relevant_offers_to_show_on_board = offer_queries.get_relevant_offers_for_user(
        current_user)
    offer_form = forms.OfferSelectForm(
        queryset=relevant_offers_to_show_on_board, data=get_params)
    offer_form.full_clean()
    context["offer_select_form"] = offer_form

    selected_offer = offer_form.cleaned_data.get("offer")
    commissions = commission_queries.get_dashboard_commissions(
        current_user,
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


class CreatorDashboard(LoginRequiredMixin, generic.FormView):
    template_name = "furfolio/dashboards/creator.html"
    form_class = forms.OfferSelectForm

    MAX_COMMISSIONS_PER_COLUMN = 15

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        make_context_for_dashboard(
            context,
            self.request.user,
            self.MAX_COMMISSIONS_PER_COLUMN,
            self.request.GET,
        )
        return context
    

class CreatorDashboardCommissionsComponent(LoginRequiredMixin, generic.TemplateView):
    template_name = "furfolio/dashboards/commissions_component.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        make_context_for_dashboard(
            context,
            self.request.user,
            CreatorDashboard.MAX_COMMISSIONS_PER_COLUMN,
            self.request.GET,
        )
        context["next"] = self.request.GET.get("next")
        return context
