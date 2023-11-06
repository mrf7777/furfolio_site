from django.core import mail
from django.test import TestCase
from .. import models
from . import utils


class EmailCommissionsTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER)

        self.offer = utils.make_offer(
            self.user_creator, max_commissions_per_user=2)
        self.commission = utils.make_commission(
            self.user_buyer, self.offer, state=models.Commission.STATE_REVIEW)

        mail.outbox = []

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
        mail.outbox = []
        managed_commission.state = models.Commission.STATE_IN_PROGRESS
        managed_commission.save()

        self.assertEqual(len(mail.outbox), 0)

    def test_new_commission_sends_email(self):
        utils.make_commission(self.user_buyer, self.offer, validate=False)
        self.assertEqual(len(mail.outbox), 1)


class EmailOffersTestCase(TestCase):
    def setUp(self):
        self.creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR)
        self.buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER, consent_to_adult=False)
        self.buyer2 = utils.make_user(
            "buyer2", role=models.User.ROLE_BUYER, consent_to_adult=True)
        utils.make_user_follow_user(self.buyer, self.creator)
        utils.make_user_follow_user(self.buyer2, self.creator)

    def test_create_offer_emails_all_followers(self):
        utils.make_offer(self.creator)
        self.assertEqual(len(mail.outbox), 2)

    def test_create_adult_offer_emails_consenting_followers(self):
        utils.make_offer(self.creator, rating=models.Offer.RATING_ADULT)
        self.assertEqual(len(mail.outbox), 1)


class CommissionMessagesTestCase(TestCase):
    def setUp(self) -> None:
        self.user_creator = utils.make_user(
            "creator", role=models.User.ROLE_CREATOR, email="creator@test.com")
        self.user_buyer = utils.make_user(
            "buyer", role=models.User.ROLE_BUYER, email="buyer@test.com")

        self.offer = utils.make_offer(self.user_creator)
        self.commission = utils.make_commission(
            self.user_buyer, self.offer, state=models.Commission.STATE_REVIEW)

        mail.outbox = []

    def test_commission_message_sends_email(self):
        utils.make_commission_message(self.user_buyer, self.commission, "Test")

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user_creator.email, mail.outbox[0].recipients())
        self.assertNotIn(self.user_buyer.email, mail.outbox[0].recipients())
