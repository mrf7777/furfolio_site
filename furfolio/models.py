from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):
    pass


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)


class Offer(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=80,
        name="name",
        validators=[validators.MinLengthValidator(5),]
    )
    cutoff_date = models.DateTimeField(
        name="cutoff_date", default=seven_days_from_now)
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})
