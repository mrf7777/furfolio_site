
from typing import Any, Type
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import generic
from django.urls import reverse
from ..queries import commissions as commission_queries
from .. import models
from .breadcrumbs import IBreadcrumbParticipant, breadcrumb_items
from .mixins import EmailsContextMixin


class FurfolioIsClosing(generic.TemplateView):
    template_name = "furfolio/pages/furfolio_is_closing.html"


class Home(generic.TemplateView):
    template_name = "furfolio/home.html"

    def get(
            self,
            request: HttpRequest,
            *args: Any,
            **kwargs: Any) -> HttpResponse:
        if self.request.user.is_authenticated:
            return redirect("dashboard")
        else:
            return super().get(request, *args, **kwargs)


class SocialsAndContacts(EmailsContextMixin, generic.TemplateView):
    template_name = "furfolio/pages/socials_and_contacts.html"


class ExampleOfferAndCommissionMixin:
    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        example_user = models.User(
            role=models.User.ROLE_CREATOR,
            username="RedFoxCreator")
        example_offer = models.Offer(
            name="Abstract Portrait with YCH",
            description="""
                I will draw your character in a portrait.
                Your character will face the viewer.
                It takes about 5 business days to finish a commission.
            """,
            author=example_user,
            min_price=20,
            max_price=30,
            slots=7,
        )
        context["example_offer"] = example_offer

        example_buyer = models.User(
            role=models.User.ROLE_BUYER,
            username="BuyerWolf")
        example_commission = models.Commission(
            commissioner=example_buyer,
            offer=example_offer,
            initial_request_text="""
            This looks cool! I want you to make a portrait of my character using rectangles.
            My character reference sheet is attached as a photo.
            """,
        )
        context["example_commission"] = example_commission

        return context


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


class Legal(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/legal.html"

    def breadcrumb_name():
        return "Legal"

    def breadcrumb_parent():
        return Help

    def breadcrumb_url():
        return reverse("legal")


class TermsOfService(
        EmailsContextMixin,
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


class Credit(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/credit.html"

    def breadcrumb_name():
        return "Credit"

    def breadcrumb_parent():
        return Legal

    def breadcrumb_url():
        return reverse("credit")


class GettingStarted(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/getting_started.html"

    def breadcrumb_name():
        return "Getting Started"

    def breadcrumb_parent():
        return Help

    def breadcrumb_url():
        return reverse("getting_started")


class WelcomeToFurfolio(
        ExampleOfferAndCommissionMixin,
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/welcome_to_furfolio.html"

    def breadcrumb_name():
        return "Welcome to Furfolio"

    def breadcrumb_parent():
        return GettingStarted

    def breadcrumb_url():
        return reverse("welcome_to_furfolio")


class WhatIsFurfolio(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/what_is_furfolio.html"

    def breadcrumb_name():
        return "What is Furfolio"

    def breadcrumb_parent():
        return GettingStarted

    def breadcrumb_url():
        return reverse("what_is_furfolio")


class OffersAndCommissions(
    ExampleOfferAndCommissionMixin,
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant,
):
    template_name = "furfolio/pages/offers_and_commissions.html"

    def breadcrumb_name():
        return "Offers and Commissions"

    def breadcrumb_parent():
        return GettingStarted

    def breadcrumb_url():
        return reverse("offers_and_commissions")


class Reference(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/reference.html"

    def breadcrumb_name():
        return "Reference"

    def breadcrumb_parent():
        return Help

    def breadcrumb_url():
        return reverse("reference")


class OfferReference(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/offer_reference.html"

    def breadcrumb_name():
        return "Offers"

    def breadcrumb_parent():
        return Reference

    def breadcrumb_url():
        return reverse("offer_reference")


class CommissionReference(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/commission_reference.html"

    def breadcrumb_name():
        return "Commissions"

    def breadcrumb_parent():
        return Reference

    def breadcrumb_url():
        return reverse("commission_reference")


class CommissionSearchHelpScenario:
    def __init__(self, scenario: str,
                 commission_query: commission_queries.CommissionsSearchQuery):
        self.scenario = scenario
        self.commission_query = commission_query


class CommissionSearchHelp(
        BreadcrumbContextMixin,
        generic.TemplateView,
        IBreadcrumbParticipant):
    template_name = "furfolio/pages/commission_search.html"

    def breadcrumb_name():
        return "Commission Search"

    def breadcrumb_parent():
        return Reference

    def breadcrumb_url():
        return reverse("commission_search_help")

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


class LocalizationReference(BreadcrumbContextMixin,
                            generic.TemplateView,
                            IBreadcrumbParticipant):
    template_name = "furfolio/pages/localization.html"

    def breadcrumb_name():
        return "Website Localization"

    def breadcrumb_parent():
        return Reference

    def breadcrumb_url():
        return reverse("localization_reference")
