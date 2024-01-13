from email.policy import default
from model_utils import FieldTracker
from django.db import models
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core import validators
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
import math

from .utils import image_resize, seven_days_from_now
from .content_rating import RATING_TO_CHOICES, RATING_GENERAL, RATING_ADULT
from .. import validators as furfolio_validators
from .. import mixins
from ..queries import commissions as commission_queries
from ..queries import offers as offer_queries
from ..queries import notifications as notification_queries


class SupportTicket(models.Model):
    STATE_OPEN = "OPEN"
    STATE_INVESTIGATING = "INVESTIGATING"
    STATE_CLOSED = "CLOSED"
    STATE_CHOICES = [
        (STATE_OPEN, "Open"),
        (STATE_INVESTIGATING, "Investigating"),
        (STATE_CLOSED, "Closed"),
    ]
    
    DESCRIPTION_MAX_LENGTH = math.ceil(settings.AVERAGE_CHARACTERS_PER_WORD * 5000)
    DESCRIPTION_MIN_LENGTH = math.ceil(settings.AVERAGE_CHARACTERS_PER_WORD * 10)
    
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    state = models.CharField(
        max_length=13,
        choices=STATE_CHOICES,
        default=STATE_OPEN,
    )
    title = models.CharField(
        max_length=100,
        validators=[validators.MinLengthValidator(5)],
        help_text="Summarize your issue with a few words. Must be between 5 and 100 characters.",
    )
    description = models.TextField(
        max_length=DESCRIPTION_MAX_LENGTH,
        validators=[validators.MinLengthValidator(DESCRIPTION_MIN_LENGTH)],
        help_text=mark_safe(
            """
            Please describe your issue in detail.
            <br>
            If possible, please answer the following questions:
            <ul>
                <li>
                    What is the issue?
                </li>
                <li>
                    Where can we see this issue? (commission chat, published offers, etc.)
                </li>
                <li>
                    When did the issue happen or start?
                </li>
                <li>
                    Who is involved? (You, another user, a group of users, etc.)
                </li>
            </ul>
            """
        ),
    )
    
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)