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


class EmailOnOfferCreateTestCase(TestCase):
    def setUp(self) -> None:
        self.creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR, email="creator@test.com")
        self.buyer1 = utils.make_user(
            "buyer1", role=models.User.ROLE_BUYER, email="buyer1@test.com")
        self.buyer2 = utils.make_user(
            "buyer2", role=models.User.ROLE_BUYER, email="buyer2@test.com")
        utils.make_user_follow_user(self.buyer1, self.creator)
        utils.make_user_follow_user(self.buyer2, self.creator)

    def test_email_on_offer_create(self):
        utils.make_offer(self.creator)
        self.assertEqual(len(mail.outbox), 2)
