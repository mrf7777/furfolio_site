
from typing import Any
from django.views import generic
from ..queries import commissions as commission_queries
from .. import models

class TermsOfService(generic.TemplateView):
    template_name = "furfolio/pages/terms_of_service.html"


class PrivacyPolicy(generic.TemplateView):
    template_name = "furfolio/pages/privacy_policy.html"


class Help(generic.TemplateView):
    template_name = "furfolio/pages/help/help.html"


class WhatIsFurfolio(generic.TemplateView):
    template_name = "furfolio/pages/help/what_is_furfolio.html"


class CommissionSearchHelpScenario:
    def __init__(self, scenario: str,
                 commission_query: commission_queries.CommissionsSearchQuery):
        self.scenario = scenario
        self.commission_query = commission_query


class CommissionSearchHelp(generic.TemplateView):
    template_name = "furfolio/pages/help/commission_search.html"

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
