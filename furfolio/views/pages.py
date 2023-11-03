
from typing import Any, Type
from django.views import generic
from django.urls import reverse
from ..queries import commissions as commission_queries
from .. import models
from .breadcrumbs import IBreadcrumbParticipant, breadcrumb_items


class BreadcrumbContextMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["breadcrumbs"] = breadcrumb_items(self.__class__)
        return context


class Help(generic.TemplateView, IBreadcrumbParticipant):
    template_name = "furfolio/pages/help.html"

    def breadcrumb_name() -> str:
        return "Help"

    def breadcrumb_parent() -> Type[IBreadcrumbParticipant] | None:
        return None

    def breadcrumb_url():
        return reverse("help")


class Error413(generic.TemplateView):
    template_name = "413.html"


class Legal(BreadcrumbContextMixin, generic.TemplateView, IBreadcrumbParticipant):
    template_name="furfolio/pages/legal.html"

    def breadcrumb_name():
        return "Legal"
    
    def breadcrumb_parent():
        return Help
    
    def breadcrumb_url():
        return reverse("legal")


class TermsOfService(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/terms_of_service.html"

    def breadcrumb_name() -> str:
        return "Terms of Service"

    def breadcrumb_parent() -> Type[IBreadcrumbParticipant] | None:
        return Legal

    def breadcrumb_url():
        return reverse("terms_of_service")


class PrivacyPolicy(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/privacy_policy.html"

    def breadcrumb_name():
        return "Privacy Policy"

    def breadcrumb_parent():
        return Legal

    def breadcrumb_url():
        return reverse("privacy_policy")


class Credit(BreadcrumbContextMixin, generic.TemplateView, IBreadcrumbParticipant):
    template_name = "furfolio/pages/credit.html"

    def breadcrumb_name():
        return "Credit"

    def breadcrumb_parent():
        return Legal

    def breadcrumb_url():
        return reverse("credit")


class WhatIsFurfolio(generic.TemplateView):
    template_name = "furfolio/pages/what_is_furfolio.html"


class OffersAndCommissions(generic.TemplateView):
    template_name = "furfolio/pages/offers_and_commissions.html"


class CommissionSearchHelpScenario:
    def __init__(self, scenario: str,
                 commission_query: commission_queries.CommissionsSearchQuery):
        self.scenario = scenario
        self.commission_query = commission_query


class CommissionSearchHelp(generic.TemplateView):
    template_name = "furfolio/pages/commission_search.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["commission_search_scenarios"] = [
            CommissionSearchHelpScenario(
                "All commissions in review",
                commission_queries.CommissionsSearchQuery(
                    review=True,
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions from offer with id 1234",
                commission_queries.CommissionsSearchQuery(
                    offer=1234
                )
            ),
            CommissionSearchHelpScenario(
                "Self-managed commissions",
                commission_queries.CommissionsSearchQuery(
                    self_managed=True,
                )
            ),
            CommissionSearchHelpScenario(
                "Accepted or finished commissions",
                commission_queries.CommissionsSearchQuery(
                    accepted=True,
                    closed=True,
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions with newest first",
                commission_queries.CommissionsSearchQuery(
                    sort=models.Commission.SORT_CREATED_DATE
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions sorted by updated date in ascending order",
                commission_queries.CommissionsSearchQuery(
                    sort=models.Commission.SORT_UPDATED_DATE,
                    order="a",
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions requested by user 'RedFox'",
                commission_queries.CommissionsSearchQuery(
                    commissioner="RedFox"
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions of an Offer published by 'CreatorMan'",
                commission_queries.CommissionsSearchQuery(
                    creator="CreatorMan"
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions from other users, from a specific offer, that are rejected or finished, sorted by created date",
                commission_queries.CommissionsSearchQuery(
                    self_managed=False,
                    offer=4321,
                    rejected=True,
                    closed=True,
                    sort=models.Commission.SORT_CREATED_DATE,
                )
            ),
        ]

        return context
