
from typing import Any
from django.views import generic
from ..queries import commissions as commission_queries


class TermsOfService(generic.TemplateView):
    template_name = "furfolio/pages/terms_of_service.html"


class PrivacyPolicy(generic.TemplateView):
    template_name = "furfolio/pages/privacy_policy.html"


class CommissionSearchHelpScenario:
    def __init__(self, scenario: str, commission_query: commission_queries.CommissionsSearchQuery):
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
                    current_user=None,
                    review=True,
                )
            ),
            CommissionSearchHelpScenario(
                "In progress commissions from offer with id 1234",
                commission_queries.CommissionsSearchQuery(
                    current_user=None,
                    in_progress=True,
                    offer=1234
                )
            ),
            CommissionSearchHelpScenario(
                "Self-managed commissions",
                commission_queries.CommissionsSearchQuery(
                    current_user=None,
                    self_managed=True,
                )
            ),
            CommissionSearchHelpScenario(
                "Accepted or finished commissions",
                commission_queries.CommissionsSearchQuery(
                    current_user=None,
                    accepted=True,
                    closed=True,
                )
            ),
            CommissionSearchHelpScenario(
                "Commissions from other users, from a specific offer, that are rejected",
                commission_queries.CommissionsSearchQuery(
                    current_user=None,
                    self_managed=False,
                    offer=4321,
                    rejected=True,
                )
            ),
        ]

        return context
