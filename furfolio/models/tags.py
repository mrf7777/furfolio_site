from django.db import models
from django.conf import settings
from django.urls import reverse
import math

from .content_rating import RATING_TO_CHOICES, RATING_GENERAL
from .. import validators as furfolio_validators
from .. import mixins


class TagCategory(models.Model):
    DESCRIPTION_MAX_LENGTH = math.ceil(
        settings.AVERAGE_CHARACTERS_PER_WORD * 1000)

    name = models.CharField(
        unique=True,
        name="name",
        verbose_name="Name",
        max_length=32,
    )
    description = models.TextField(
        name="description",
        max_length=DESCRIPTION_MAX_LENGTH,
        default="",
        blank=True,
    )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tag_category_detail", kwargs={"name": self.name})


class Tag(mixins.GetFullUrlMixin, models.Model):
    DESCRIPTION_MAX_LENGTH = math.ceil(
        settings.AVERAGE_CHARACTERS_PER_WORD * 1000)

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        name="author",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        TagCategory,
        name="category",
        verbose_name="Category",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    name = models.CharField(
        unique=True,
        name="name",
        verbose_name="Name",
        max_length=38,
        validators=[furfolio_validators.validate_tag_name,]
    )
    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        name="description",
        verbose_name="Description",
        default="",
        blank=True,
    )
    rating = models.CharField(
        name="rating",
        max_length=3,
        choices=RATING_TO_CHOICES,
        default=RATING_GENERAL,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self) -> str:
        return self.name

    def friendly_category_string(self) -> str:
        if self.category:
            return self.category
        else:
            return ""

    def get_absolute_url(self):
        return reverse("tag_detail", kwargs={"name": self.name})
