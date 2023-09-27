from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
import math
from . import validators as furfolio_validators


AVERAGE_CHARACTERS_PER_WORD = 4.7


class User(AbstractUser):
    ROLE_BUYER = "BUYER"
    ROLE_CREATOR = "CREATOR"
    ROLE_CHOICES = [
        (ROLE_BUYER, "Buyer"),
        (ROLE_CREATOR, "Creator"),
    ]
    avatar = models.ImageField(
        name="avatar",
        blank=True,
        help_text="Avatars are optional. Your avatar must be 64 by 64 pixels.",
        validators=[furfolio_validators.validate_profile_image_is_right_size,],
    )
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=ROLE_BUYER,
        help_text="Your role on this platform. This is used to optimize your experience and to let others know how you want to use this website."
    )

    def get_absolute_url(self):
        return reverse("user", kwargs={"username": self.username})


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)


# limit offer description to about 1000 words
OFFER_DESCRIPTION_MAX_LENGTH = math.ceil(AVERAGE_CHARACTERS_PER_WORD * 1000)
# offer description must have at least about 4 words
OFFER_DESCRIPTION_MIN_LENGTH = math.floor(AVERAGE_CHARACTERS_PER_WORD * 4)


class Offer(models.Model):
    RATING_GENERAL = "GEN"
    RATING_MATURE = "MAT"
    RATING_ADULT = "ADL"
    RATING_TO_CHOICES = [
        (RATING_GENERAL, "General"),
        (RATING_MATURE, "Mature"),
        (RATING_ADULT, "Adult"),
    ]
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=80,
        name="name",
        help_text="Must be between 5 and 80 characters long.",
        validators=[validators.MinLengthValidator(5),]
    )
    description = models.TextField(
        max_length=OFFER_DESCRIPTION_MAX_LENGTH,
        name="description",
        help_text="Describes the details of the offer.",
        validators=[validators.MinLengthValidator(
            OFFER_DESCRIPTION_MIN_LENGTH),],
        default="",
    )
    cutoff_date = models.DateTimeField(
        name="cutoff_date",
        default=seven_days_from_now,
        validators=[
            furfolio_validators.validate_datetime_not_in_past,
            furfolio_validators.validate_datetime_at_least_12_hours,
        ],
    )
    forced_closed = models.BooleanField(
        name="forced_closed",
        help_text="Indicates that the offer is closed, regardless if the cutoff date has passed or not.",
        default=False,
    )
    thumbnail = models.ImageField(name="thumbnail", blank=True, null=True)
    rating = models.CharField(
        name="rating",
        max_length=3,
        choices=RATING_TO_CHOICES,
        default=RATING_GENERAL,
    )
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})

    def is_closed(self):
        if self.forced_closed:
            return True
        elif self.cutoff_date < timezone.now():
            return True
        return False


# limit initial request text to about 800 words
COMMISSION_INITIAL_REQUEST_TEXT_MAX_LENGTH = math.ceil(
    AVERAGE_CHARACTERS_PER_WORD * 800)


class Commission(models.Model):
    STATE_REVIEW = "REVIEW"
    STATE_ACCEPTED = "ACCEPTED"
    STATE_IN_PROGRESS = "IN_PROGRESS"
    STATE_CLOSED = "CLOSED"
    STATE_CHOICES = [
        (STATE_REVIEW, "Review"),
        (STATE_ACCEPTED, "Accepted"),
        (STATE_IN_PROGRESS, "In Progress"),
        (STATE_CLOSED, "Closed"),
    ]
    commissioner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        name="commissioner",
        on_delete=models.CASCADE,
    )
    offer = models.ForeignKey(
        Offer,
        name="offer",
        on_delete=models.CASCADE
    )
    initial_request_text = models.TextField(
        name="initial_request_text",
        help_text="First-pass requirements for the commission.",
        max_length=COMMISSION_INITIAL_REQUEST_TEXT_MAX_LENGTH,
        default="",
        verbose_name="Initial Requirements"
    )
    attachment = models.FileField(
        name="attachment",
        help_text="Optional file that is part of this request.",
        blank=True,
    )
    state = models.CharField(
        name="state",
        max_length=11,
        choices=STATE_CHOICES,
        default=STATE_REVIEW,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return "Id: %i. \"%s\" requested \"%s\"." % (self.id, self.commissioner.username, self.offer.name)

    def get_absolute_url(self):
        return reverse("commission_detail", kwargs={"pk": self.pk})
