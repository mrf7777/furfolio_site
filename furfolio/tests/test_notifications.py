from django.core import mail
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
        self.assertEquals(models.ChatMessageNotification.objects.all().count(), 1)
        self.assertEquals(models.Notification.objects.all().count(), 1)


    def test_delete_chat_message_notification_deletes_parent(self):
        self.message = utils.make_chat_message(self.chat, self.user1)
        
        # before delete
        self.assertEquals(models.ChatMessageNotification.objects.all().count(), 1)
        number_notifications_pre_delete = models.Notification.objects.all().count()
        
        # delete
        message_notification = models.ChatMessageNotification.objects.first()
        message_notification.delete()
        
        # confirm parent notification was also deleted
        self.assertEquals(models.ChatMessageNotification.objects.all().count(), 0)
        self.assertEquals(models.Notification.objects.all().count(), number_notifications_pre_delete - 1)
