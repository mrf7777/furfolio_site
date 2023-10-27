from django.test import TestCase, Client
from ..models import Commission, User, Offer
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from .. import models
from . import utils
import datetime


class PagesTestCase(TestCase):
    def test_privacy_policy(self):
        response = self.client.get(reverse("privacy_policy"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_terms_of_service(self):
        response = self.client.get(reverse("terms_of_service"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get(reverse("home"), follow=True)
        self.assertEqual(response.status_code, 200)


class CommissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(
            self.user_buyer, self.offer, state=models.Commission.STATE_REVIEW)
