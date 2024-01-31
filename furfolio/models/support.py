from django.db import models
from django.conf import settings
from django.core import validators
from django.urls import reverse
from django.utils.safestring import mark_safe
from model_utils import FieldTracker

import math

from .. import mixins
from ..queries import notifications as notification_queries
from ..queries import chat as chat_queries


class SupportTicket(mixins.GetFullUrlMixin, models.Model):
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
            If possible, please answer as many of the following questions as possible:
            <ul>
                <li>
                    What is the issue?
                </li>
                <li>
                    Where can we see this issue? Add a URL or a link. (commission chat, published offers, etc.)
                </li>
                <li>
                    When did the issue happen or start?
                </li>
                <li>
                    Who is involved? (You, another user, a group of users, etc.)
                </li>
                <li>
                    How did the issue happen?
                </li>
            </ul>
            """
        ),
    )
    
    tracker = FieldTracker()
    
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def get_absolute_url(self):
        return reverse("support_ticket_detail", kwargs={"pk": self.pk})

    def __str__(self) -> str:
        states_as_dict = dict(self.STATE_CHOICES)
        state_human_text = states_as_dict[self.state]
        return f"({state_human_text}) \"{self.title}\" by {self.author.username}"

    def friendly_state_text(self) -> str:
        states_as_dict = dict(self.STATE_CHOICES)
        return states_as_dict[self.state]
    
    def save(self, *args, **kwargs) -> None:
        saved: bool = False
        if self.should_notify_state_changed():
            super().save(*args, **kwargs)
            saved = True
            notification_queries.create_support_ticket_state_notification_for_author(self)
            
        if not saved:
            super().save(*args, **kwargs)
            saved = True

    def should_notify_state_changed(self) -> bool:
        return self.tracker.previous("state") is not None and self.tracker.has_changed("state")

    def get_chat(self):
        return chat_queries.get_support_ticket_chat_by_support_ticket(self)
