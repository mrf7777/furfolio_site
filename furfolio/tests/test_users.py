from ctypes import util
from django.test import TestCase
from ..models import Commission, User, Offer
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core import mail
from . import utils
from .. import utils as furfolio_utils
from .. import models
import datetime


class GetFollowedUsersTestCase(TestCase):
    def setUp(self) -> None:
        self.user1 = utils.make_user("user1")
        self.user2 = utils.make_user("user2")
        utils.make_user_follow_user(self.user1, self.user2)
        
    def test_get_followed_users(self):
        followed_users = map(lambda u: u.username, self.user1.get_followed_users())
        self.assertIn(self.user2.username, followed_users)
