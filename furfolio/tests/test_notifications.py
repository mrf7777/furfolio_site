from django.test import TestCase
from .. import models
from . import utils


class ChatMessageNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1")
        self.user2 = utils.make_user("user2")
        self.chat = utils.make_chat()
        utils.add_chat_participant(self.chat, self.user1)
        utils.add_chat_participant(self.chat, self.user2)

    def test_chat_message_created_chat_message_notification(self):
        self.message = utils.make_chat_message(self.chat, self.user1)
        self.assertEquals(
            models.ChatMessageNotification.objects.all().count(), 1)

    def test_delete_chat_message_notification_deletes_parent(self):
        self.message = utils.make_chat_message(self.chat, self.user1)

        # before delete
        self.assertEquals(
            models.ChatMessageNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        message_notification = models.ChatMessageNotification.objects.first()
        message_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.ChatMessageNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)


class OfferPostedNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1", role=models.User.ROLE_CREATOR)
        self.user2 = utils.make_user("user2", role=models.User.ROLE_BUYER)
        utils.make_user_follow_user(self.user2, self.user1)

    def test_offer_creates_offer_posted_notification(self):
        self.offer = utils.make_offer(self.user1)
        self.assertEquals(
            models.OfferPostedNotification.objects.all().count(), 1)

    def test_delete_offer_posted_notification_deletes_parent(self):
        self.offer = utils.make_offer(self.user1)

        # before delete
        self.assertEquals(
            models.OfferPostedNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        offer_notification = models.OfferPostedNotification.objects.first()
        offer_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.OfferPostedNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)


class CommissionStateNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1", role=models.User.ROLE_CREATOR)
        self.user2 = utils.make_user("user2", role=models.User.ROLE_BUYER)
        self.offer = utils.make_offer(self.user1)
        self.commission = utils.make_commission(
            self.user2, self.offer, models.Commission.STATE_REVIEW)

    def test_state_change_creates_commission_state_notification(self):
        commission = models.Commission.objects.first()
        commission.state = models.Commission.STATE_ACCEPTED
        commission.save()
        self.assertEqual(
            models.CommissionStateNotification.objects.all().count(), 1)

    def test_delete_state_change_notification_deletes_parent(self):
        commission = models.Commission.objects.first()
        commission.state = models.Commission.STATE_ACCEPTED
        commission.save()

        # before delete
        self.assertEquals(
            models.CommissionStateNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        state_notification = models.CommissionStateNotification.objects.first()
        state_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.CommissionStateNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)


class CommissionCreatedNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1", role=models.User.ROLE_CREATOR)
        self.user2 = utils.make_user("user2", role=models.User.ROLE_BUYER)
        self.offer = utils.make_offer(self.user1)

    def test_commission_created_creates_commission_created_notification(self):
        self.commission = utils.make_commission(
            self.user2, self.offer, models.Commission.STATE_REVIEW)
        self.assertEqual(
            models.CommissionCreatedNotification.objects.all().count(), 1)

    def test_delete_commission_created_notification_deletes_parent(self):
        self.commission = utils.make_commission(
            self.user2, self.offer, models.Commission.STATE_REVIEW)

        # before delete
        self.assertEquals(
            models.CommissionCreatedNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        commission_created_notification = models.CommissionCreatedNotification.objects.first()
        commission_created_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.CommissionCreatedNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)


class UserFollowedNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1", role=models.User.ROLE_CREATOR)
        self.user2 = utils.make_user("user2", role=models.User.ROLE_BUYER)

    def test_user_followed_creates_user_followed_notification(self):
        utils.make_user_follow_user(self.user1, self.user2)
        self.assertEqual(
            models.UserFollowedNotification.objects.all().count(), 1)

    def test_delete_user_followed_notification_deletes_parent(self):
        utils.make_user_follow_user(self.user1, self.user2)

        # before delete
        self.assertEquals(
            models.UserFollowedNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        user_followed_notification = models.UserFollowedNotification.objects.first()
        user_followed_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.UserFollowedNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)


class SupportTicketStateNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1", role=models.User.ROLE_CREATOR)
        self.support_ticket = utils.make_support_ticket(
            self.user1, state=models.SupportTicket.STATE_OPEN)

    def test_support_ticket_state_changed_creates_notification(self):
        self.support_ticket.state = models.SupportTicket.STATE_INVESTIGATING
        self.support_ticket.full_clean()
        self.support_ticket.save()
        self.assertEqual(
            models.SupportTicketStateNotification.objects.all().count(), 1)

    def test_delete_support_ticket_state_notification_deletes_parent(self):
        self.support_ticket.state = models.SupportTicket.STATE_INVESTIGATING
        self.support_ticket.full_clean()
        self.support_ticket.save()

        # before delete
        self.assertEquals(
            models.SupportTicketStateNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()

        # delete
        support_ticket_state_notification = models.SupportTicketStateNotification.objects.first()
        support_ticket_state_notification.delete()

        # confirm parent notification was also deleted
        self.assertEquals(
            models.SupportTicketStateNotification.objects.all().count(), 0)
        self.assertEquals(
            models.Notification.objects.all().count(),
            number_notifications_pre_delete - 1)
