from PIL import Image
import PIL.ImageFile
from io import BytesIO
from pathlib import Path
from model_utils import FieldTracker
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.core import validators
from django.core.files import File
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import math

from .utils import image_resize
from .offers import Offer
from .. import validators as furfolio_validators
from .. import mixins
from ..queries import commissions as commission_queries
from ..queries import users as user_queries
from ..queries import offers as offer_queries
from ..queries import notifications as notification_queries


class User(mixins.GetFullUrlMixin, AbstractUser):
    MAX_PROFILE_LENGTH = math.ceil(settings.AVERAGE_CHARACTERS_PER_WORD * 1000)

    ROLE_BUYER = "BUYER"
    ROLE_CREATOR = "CREATOR"
    ROLE_CHOICES = [
        (ROLE_BUYER, "Buyer"),
        (ROLE_CREATOR, "Creator"),
    ]
    AVATAR_SIZE_PIXELS = (64, 64)
    avatar = models.ImageField(
        name="avatar",
        blank=True,
        help_text="Avatars are optional. Your avatar will be resized to 64 by 64 pixels.",
        validators=[
            furfolio_validators.validate_profile_image_is_right_size,
            furfolio_validators.validate_avatar_has_max_size,
        ])
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=ROLE_BUYER,
        help_text="Your role on this platform. This is used to optimize your experience and to let others know how you want to use this website."
    )
    consent_to_adult_content = models.BooleanField(
        name="consent_to_adult_content",
        verbose_name="Consent to see adult content",
        help_text=mark_safe(
            "Indicate if you would like to see adult content on this website. If not indicated, you will not see adult content.<br> If you consent, you agree that you are legally allowed to view \"adult\" content."),
        default=False,
    )
    profile = models.TextField(
        name="profile",
        verbose_name="Profile Description",
        max_length=MAX_PROFILE_LENGTH,
        blank=True,
        help_text="This will display on you profile page. Use this to describe yourself."
    )

    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    tracker = FieldTracker()

    class Meta:
        indexes = [
            GinIndex(fields=["username",], fastupdate=False,
                     name="user_username_index")
        ]

    def save(self, *args, **kwargs) -> None:
        if self.avatar and self.tracker.has_changed("avatar"):
            image_resize(
                self.avatar,
                User.AVATAR_SIZE_PIXELS[0],
                User.AVATAR_SIZE_PIXELS[1],
                transparency_remove=True,
                fit_in_center=True)
        super(User, self).save(*args, **kwargs)

    def get_following_users(self):
        return user_queries.get_users_following_user(self)

    def get_followed_users(self):
        return user_queries.get_followed_users(self)

    def get_absolute_url(self):
        return reverse("user", kwargs={"username": self.username})

    def get_num_unread_notifications(self):
        return notification_queries.get_num_unread_notifications_for_user(self)

    def can_commission_offer(self, offer: 'Offer'):
        if self == offer.author:
            return True
        elif offer.is_closed():
            return False
        elif offer.has_max_review_commissions():
            return False
        elif commission_queries.get_commissions_for_commissioner_and_offer(self, offer).count() >= offer.max_commissions_per_user:
            return False
        else:
            return True


class UserFollowingUser(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed")

    created_date = models.DateTimeField(
        name="created_date",
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if self.pk is None:
            super().save(*args, **kwargs)
            notification_queries.create_user_followed_notification_using_user_following_user(self)
        else:
            super().save(*args, **kwargs)
        

    def __str__(self):
        return f"{self.follower.username} is following {self.followed.username}"
