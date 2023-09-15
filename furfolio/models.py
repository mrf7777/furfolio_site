from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from . import validators as furfolio_validators


class User(AbstractUser):
    avatar = models.ImageField(
        name="avatar",
        blank=True,
        help_text="Your avatar must be 100 by 100 pixels.",
        validators=[furfolio_validators.validate_profile_image_is_right_size,],
    )


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)


class Offer(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=80,
        name="name",
        help_text="Must be between 5 and 80 characters long.",
        validators=[validators.MinLengthValidator(5),]
    )
    cutoff_date = models.DateTimeField(
        name="cutoff_date",
        default=seven_days_from_now,
        validators=[
            furfolio_validators.validate_datetime_not_in_past,
            furfolio_validators.validate_datetime_at_least_12_hours,
        ],
    )
    thumbnail = models.ImageField(name="thumbnail", blank=True, null=True)
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})
