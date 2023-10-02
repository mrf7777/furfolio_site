from django.test import TestCase, Client
from ..models import Commission, User, Offer
from django.utils import timezone
from django.urls import reverse
from django.core.exceptions import ValidationError
from .. import models
import datetime


class PagesRenderTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_privacy_policy(self):
        response = self.client.get(reverse("privacy_policy"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_terms_of_service(self):
        response = self.client.get(reverse("terms_of_service"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_home(self):
        response = self.client.get(reverse("home"), follow=True)
        self.assertEqual(response.status_code, 200)


class OffersSignedInTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = models.User(
            username="creator",
            password="admin",
        )
        self.user.full_clean()
        self.user.save()
        self.offer = models.Offer(
            author=self.user,
            name="Offer",
            description="This is an offer created by a user.",
        )
        self.offer.full_clean()
        self.offer.save()
        self.client.login(username="creator", password="admin")

    def test_offer_list(self):
        response = self.client.get(reverse("offer_list"), follow=True)
        self.assertContains(response, self.offer.description)

    def test_offer_create(self):
        response = self.client.get(reverse("create_offer"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_update(self):
        response = self.client.get(
            reverse("update_offer", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_delete(self):
        response = self.client.get(
            reverse("delete_offer", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_detail(self):
        response = self.client.get(
            reverse("offer_detail", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_offers(self):
        response = self.client.get(
            reverse("user_offers", args=[self.user.username,]), follow=True)
        self.assertContains(response, self.offer.name)


class UsersSignedInTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = models.User(
            username="creator",
            password="admin",
        )
        self.user.full_clean()
        self.user.save()
        self.offer = models.Offer(
            author=self.user,
            name="Offer",
            description="This is an offer created by a user.",
        )
        self.offer.full_clean()
        self.offer.save()
        self.client.login(username="creator", password="admin")

    def test_user_page(self):
        response = self.client.get(
            reverse("user", args=[self.user.username,]), follow=True)
        self.assertContains(response, self.user.username)

    def test_user_update(self):
        response = self.client.get(
            reverse("user", args=[self.user.username,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        response = self.client.get(reverse("user_list"), follow=True)
        self.assertContains(response, self.user.username)


class CreatorDashboardTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user_creator = models.User(
            username="creator",
            password="admin",
            role=models.User.ROLE_CREATOR,
        )
        self.user_creator.full_clean()
        self.user_creator.save()
        self.user_buyer = models.User(
            username="buyer",
            password="admin",
            role=models.User.ROLE_BUYER,
        )
        self.user_buyer.full_clean()
        self.user_buyer.save()
        self.offer = models.Offer(
            author=self.user_creator,
            name="Offer",
            description="This is an offer created by a user.",
        )
        self.offer.full_clean()
        self.offer.save()
        self.commission = models.Commission(
            commissioner=self.user_buyer,
            offer=self.offer,
            initial_request_text="I want that offer.",
        )
        self.commission.full_clean()
        self.commission.save()
        self.client.force_login(self.user_creator)

    def test_creator_dashboard(self):
        response = self.client.get(reverse("dashboard"), follow=True)
        self.assertContains(response, self.commission.initial_request_text)
