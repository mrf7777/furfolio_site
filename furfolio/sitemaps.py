from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Offer
from .models import User


class StaticSiteLocationMixin:
    def location(self, item):
        return reverse(item)


class HomePageSitemap(StaticSiteLocationMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "home",
        ]


class StaticSitemap(StaticSiteLocationMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.2

    def items(self):
        return [
            "terms_of_service",
            "privacy_policy",
            "help",
            "what_is_furfolio",
            "offers_and_commissions",
            "commission_search_help"
        ]


class OfferSitemap(Sitemap):
    changefreq = "hourly"
    priority = 0.8

    def items(self):
        return Offer.objects.all()

    def lastmod(self, offer: Offer):
        return offer.updated_date


class UserSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return User.objects.all()

    def lastmod(self, user: User):
        return user.updated_date


sitemaps = {
    "home_page": HomePageSitemap,
    "static": StaticSitemap,
    "offers": OfferSitemap,
    "users": UserSitemap,
}
