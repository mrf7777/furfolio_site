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


class OffersSignedInTestCase(TestCase):
    def setUp(self) -> None:
        self.user = utils.make_user("creator", role=models.User.ROLE_CREATOR)
        self.offer = utils.make_offer(
            user=self.user, name="Offer", description="This is an offer created by a user")

    def test_offer_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("offer_list"), follow=True)
        self.assertContains(response, self.offer.description)

    def test_offer_create(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("create_offer"), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_update(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("update_offer", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_delete(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("delete_offer", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_offer_detail(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("offer_detail", args=[self.offer.pk,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_offers(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("user_offers", args=[self.user.username,]), follow=True)
        self.assertContains(response, self.offer.name)


class UsersInTestCase(TestCase):
    def setUp(self) -> None:
        self.user = utils.make_user("creator", role=models.User.ROLE_CREATOR)
        self.offer = utils.make_offer(
            user=self.user, name="Offer", description="This is an offer created by a user")

    def test_user_page(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("user", args=[self.user.username,]), follow=True)
        self.assertContains(response, self.user.username)
        self.assertContains(response, reverse(
            "user", args=[self.user.username]))

    def test_user_update(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("user", args=[self.user.username,]), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_user_list(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("user_list"), follow=True)
        self.assertContains(response, self.user.username)
        self.assertContains(response, reverse(
            "user", args=[self.user.username]))


class CreatorDashboardTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(self.user_buyer, self.offer)

    def test_creator_dashboard(self):
        self.client.force_login(self.user_creator)
        response = self.client.get(reverse("dashboard"), follow=True)
        self.assertContains(response, self.commission.initial_request_text)
        self.assertContains(response, reverse("buyer_dashboard"))


class BuyerBashboardTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(self.user_buyer, self.offer)

    def test_buyer_dashboard(self):
        self.client.force_login(self.user_buyer)
        response = self.client.get(reverse("dashboard"), follow=True)
        self.assertContains(response, self.commission.initial_request_text)
        self.assertContains(response, reverse("creator_dashboard"))


class CommissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(self.user_buyer, self.offer, state=models.Commission.STATE_REVIEW)

    def test_commission_detail_as_creator(self):
        self.client.force_login(self.user_creator)
        response = self.client.get(
            reverse(
                "commission_detail",
                args=[self.commission.pk]
            ),
            follow=True
        )
        self.assertContains(response, self.commission.initial_request_text)
        self.assertContains(response, reverse("commission_chat", args=[self.commission.pk]))
        self.assertContains(response, reverse("update_commission_status", args=[self.commission.pk]))
        self.assertContains(response, reverse(
            "update_commission", args=[self.commission.pk]))

    def test_commission_detail_as_buyer(self):
        self.client.force_login(self.user_buyer)
        response = self.client.get(
            reverse(
                "commission_detail",
                args=[self.commission.pk]
            ),
            follow=True
        )
        self.assertContains(response, self.commission.initial_request_text)
        self.assertContains(response, reverse("commission_chat", args=[self.commission.pk]))
        self.assertNotContains(response, reverse("update_commission_status", args=[self.commission.pk]))
        self.assertNotContains(response, reverse(
            "update_commission", args=[self.commission.pk]))

    def test_create_commission(self):
        self.client.force_login(self.user_buyer)
        response = self.client.get(
            reverse(
                "create_commission",
                args=[self.offer.pk],
            ),
            follow=True,
        )
        self.assertContains(response, self.offer.name)
        self.assertContains(response, self.user_creator.username)

    def test_update_commission(self):
        self.client.force_login(self.user_creator)
        response = self.client.get(
            reverse(
                "update_commission",
                args=[self.commission.pk]
            ),
            follow=True
        )
        self.assertContains(response, self.commission.initial_request_text)
        self.assertContains(response, self.user_buyer.username)


class CommissionChatTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(self.user_buyer, self.offer)

        self.message_buyer = utils.make_commission_message(
            self.user_buyer, self.commission, "Hi. What is your name?")
        self.message_creator = utils.make_commission_message(
            self.user_creator, self.commission, "My name is creator.")

    def test_commission_chat_as_buyer(self):
        self.client.force_login(self.user_buyer)
        response = self.client.get(
            reverse("commission_chat", args=[self.commission.pk]), follow=True)
        self.assertContains(response, self.message_buyer.message)
        self.assertContains(response, self.message_creator.message)

    def test_commission_chat_as_creator(self):
        self.client.force_login(self.user_creator)
        response = self.client.get(
            reverse("commission_chat", args=[self.commission.pk]), follow=True)
        self.assertContains(response, self.message_buyer.message)
        self.assertContains(response, self.message_creator.message)
