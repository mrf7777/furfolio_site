from ctypes import util
from django.test import TestCase
from ..models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core import mail
from . import utils
from .. import utils as furfolio_utils
from .. import models
import datetime


class MaxActiveOffersPerUserTestCase(TestCase):
    def setUp(self):
        self.user = utils.make_user("user", role=models.User.ROLE_CREATOR)

    def make_max_offers_for_user(user, amount_of_offers = models.Offer.MAX_ACTIVE_OFFERS_PER_USER):
        offers = []
        for i in range(amount_of_offers):
            offers.append(utils.make_offer(
                user,
                name=f"Offer {i}",
            ))
        return offers

    def test_author_can_update_offer_at_max_limit(self):
        offers = self.__class__.make_max_offers_for_user(self.user)
        offer = offers[0]
        offer.description = "This is a new description that has text."
        offer.full_clean()
        offer.save()

    def test_author_can_update_offer_below_offer_limit(self):
        offers = self.__class__.make_max_offers_for_user(self.user, models.Offer.MAX_ACTIVE_OFFERS_PER_USER - 1)
        offer = offers[0]
        offer.description = "This is a new description that has text."
        offer.full_clean()
        offer.save()

    def test_author_cannot_go_over_max_offer_limit(self):
        with self.assertRaises(ValidationError):
            self.__class__.make_max_offers_for_user(self.user, models.Offer.MAX_ACTIVE_OFFERS_PER_USER + 1)
