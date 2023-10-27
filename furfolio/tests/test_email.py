from django.test import TestCase, Client
from ..models import Commission, User, Offer
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core import mail
from .. import models
from . import utils
from .. import email
import datetime


class EmailCommissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(
            self.user_buyer, self.offer, state=models.Commission.STATE_REVIEW)

    def test_send_email_on_commission_state_change(self):
        self.commission.state = models.Commission.STATE_REJECTED
        self.commission.save()

        self.assertEqual(len(mail.outbox), 1)

    def test_commission_state_change_email_hyperlinks(self):
        self.commission.state = models.Commission.STATE_IN_PROGRESS
        self.commission.save()

        commission_full_url = self.commission.get_full_url()
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(commission_full_url in mail.outbox[0].body)

    def test_self_managed_commission_does_not_send_email(self):
        managed_commission = utils.make_commission(
            self.user_creator, self.offer)
        managed_commission.state = models.Commission.STATE_IN_PROGRESS
        managed_commission.save()

        self.assertEqual(len(mail.outbox), 0)


class EmailOffersTestCase(TestCase):
    def setUp(self):
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)
        utils.make_user_follow_user(self.user_buyer, self.user_creator)
        
    def test_create_offer_sends_email_to_follower(self):
        utils.make_offer(self.user_creator)
        
        self.assertEqual(len(mail.outbox), 1)
