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


class GetFollowedUsersTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = utils.make_user("user1")
        self.user2 = utils.make_user("user2")
        utils.make_user_follow_user(self.user1, self.user2)

    def test_get_followed_users(self):
        followed_users = map(
            lambda u: u.username,
            self.user1.get_followed_users())
        self.assertIn(self.user2.username, followed_users)


class CanUserCommissionOfferTestCase(TestCase):
    def setUp(self):
        self.buyer = utils.make_user("buyer", role=models.User.ROLE_BUYER)
        self.buyer2 = utils.make_user("buyer2", role=models.User.ROLE_BUYER)
        self.creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)

        self.offer = utils.make_offer(
            self.creator,
            max_review_commissions=1,
            max_commissions_per_user=1,
            validate=False)
        self.offer_forced_closed = utils.make_offer(
            self.creator,
            max_review_commissions=1,
            max_commissions_per_user=1,
            forced_closed=True,
            validate=False)
        self.offer_many_review_slots = utils.make_offer(
            self.creator,
            max_review_commissions=100,
            max_commissions_per_user=1,
            validate=False)

    def test_self_managed_commission(self):
        self.assertTrue(self.creator.can_commission_offer(self.offer))
        self.assertTrue(
            self.creator.can_commission_offer(
                self.offer_forced_closed))
        utils.make_commission(self.creator, self.offer)
        utils.make_commission(self.creator, self.offer_forced_closed)

    def test_forced_closed_offer_with_other_user(self):
        self.assertFalse(
            self.buyer.can_commission_offer(
                self.offer_forced_closed))
        with self.assertRaises(ValidationError):
            utils.make_commission(self.buyer, self.offer_forced_closed)

    def test_max_review_commissions_with_other_user(self):
        utils.make_commission(self.buyer, self.offer)
        self.assertFalse(self.buyer2.can_commission_offer(self.offer))
        with self.assertRaises(ValidationError):
            utils.make_commission(self.buyer2, self.offer)

    def test_max_commissions_per_user(self):
        utils.make_commission(self.buyer, self.offer_many_review_slots)
        self.assertFalse(
            self.buyer.can_commission_offer(
                self.offer_many_review_slots))
        with self.assertRaises(ValidationError):
            utils.make_commission(self.buyer, self.offer_many_review_slots)
