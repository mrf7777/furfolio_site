from django.db import models
from django.conf import settings
from django.core import validators
from django.utils.safestring import mark_safe
import math


class SupportTicket(models.Model):
    STATE_OPEN = "OPEN"
    STATE_INVESTIGATING = "INVESTIGATING"
    STATE_CLOSED = "CLOSED"
    STATE_CHOICES = [
        (STATE_OPEN, "Open"),
        (STATE_INVESTIGATING, "Investigating"),
        (STATE_CLOSED, "Closed"),
    ]

    DESCRIPTION_MAX_LENGTH = math.ceil(
        settings.AVERAGE_CHARACTERS_PER_WORD * 5000)
    DESCRIPTION_MIN_LENGTH = math.ceil(
        settings.AVERAGE_CHARACTERS_PER_WORD * 10)
    
    TITLE_MAX_LENGTH = 100
    TITLE_MIN_LENGTH = 5

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
        max_length=TITLE_MAX_LENGTH,
        validators=[
            validators.MinLengthValidator(TITLE_MIN_LENGTH)],
        help_text=f"Summarize your issue with a few words. Must be between {TITLE_MIN_LENGTH} and {TITLE_MAX_LENGTH} characters.",
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
