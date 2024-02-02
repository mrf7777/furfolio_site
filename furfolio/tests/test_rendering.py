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
