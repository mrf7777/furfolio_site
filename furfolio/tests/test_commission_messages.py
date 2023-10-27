from ctypes import util
from django.test import TestCase
from ..models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
from . import utils
from .. import models
from .. import utils as furfolio_utils
from ..queries import commissions as commission_queries
from ..queries import commission_messages as commission_message_queries
import datetime


class GetCommissionMessagesTestCase(TestCase):
    def setUp(self):
        self.creator = utils.make_user(
            "creator",
            role=models.User.ROLE_CREATOR,
            email="creator@test.com")
        self.buyer = utils.make_user(
            "buyer",
            role=models.User.ROLE_BUYER,
            email="buyer@test.com")
        self.offer = utils.make_offer(self.creator)
        self.commission = utils.make_commission(self.buyer, self.offer)

    def test_get_single_commission_message(self):
        message = "I want an OC too!"
        commission_message = utils.make_commission_message(
            self.buyer, self.commission, message)

        self.assertEqual(
            commission_message.message,
            commission_message_queries.get_commission_messages_for_commission(
                self.commission)[0].message)
