from django.test import TestCase
from ..models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
from . import utils
from .. import utils as furfolio_utils
from .. import models
from ..queries import commissions as commission_queries
import datetime


class ChatParticipantCanMessageTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1")
        self.user2 = utils.make_user("user2")
        self.user3 = utils.make_user("user3")
        self.chat = utils.make_chat()
        for user in [self.user1, self.user2]:
            utils.add_chat_participant(self.chat, user)
            
    def test_participating_user_message(self):
        utils.make_chat_message(self.chat, self.user1)
        
    def test_non_participating_user_cannot_message(self):
        with self.assertRaises(ValidationError):
            utils.make_chat_message(self.chat, self.user3)
            

class ChatMessageNotificationTestCase(TestCase):
    def setUp(self):
        self.user1 = utils.make_user("user1")
        self.user2 = utils.make_user("user2")
        self.user3 = utils.make_user("user3")
        self.user4 = utils.make_user("user4")
        self.chat = utils.make_chat()
        for user in [self.user1, self.user2, self.user3]:
            utils.add_chat_participant(self.chat, user)
            
    def test_message_notifies_participants(self):
        utils.make_chat_message(self.chat, self.user1)
        self.assertQuerySetEqual(
            models.ChatMessageNotification.objects.order_by("pk").all(),
            [self.user2.pk, self.user3.pk],
            transform=lambda message_noti: message_noti.notification.recipient.pk
        )