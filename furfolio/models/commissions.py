from model_utils import FieldTracker
from django.db import models
from django.conf import settings
from django.urls import reverse
import math

from .offers import Offer
from .. import validators as furfolio_validators
from .. import mixins
from ..queries import notifications as notification_queries
from ..queries import chat as chat_queries


# limit initial request text to about 800 words
COMMISSION_INITIAL_REQUEST_TEXT_MAX_LENGTH = math.ceil(
    settings.AVERAGE_CHARACTERS_PER_WORD * 800)


class Commission(mixins.CleaningMixin, mixins.GetFullUrlMixin, models.Model):
    STATE_REVIEW = "REVIEW"
    STATE_ACCEPTED = "ACCEPTED"
    STATE_IN_PROGRESS = "IN_PROGRESS"
    STATE_CLOSED = "CLOSED"
    STATE_REJECTED = "REJECTED"
    STATE_CHOICES = [
        (STATE_REVIEW, "Review"),
        (STATE_ACCEPTED, "Accepted"),
        (STATE_IN_PROGRESS, "In Progress"),
        (STATE_CLOSED, "Finished"),
        (STATE_REJECTED, "Rejected"),
    ]

    SORT_CREATED_DATE = "created_date"
    SORT_UPDATED_DATE = "updated_date"
    SORT_CHOICES = [
        (SORT_CREATED_DATE, "Created Date"),
        (SORT_UPDATED_DATE, "Updated Date"),
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
        validators=[
            furfolio_validators.validate_commission_attachment_has_max_size,
        ]
    )
    state = models.CharField(
        name="state",
        max_length=11,
        choices=STATE_CHOICES,
        default=STATE_REVIEW,
    )

    tracker = FieldTracker()

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def save(self, *args, **kwargs) -> None:
        saved: bool = False
        if self.should_notify_state_change():
            notification_queries.create_commission_state_notification_for_commissioner(
                self)
        if self.should_notify_new_commission():
            if not saved:
                super().save(*args, **kwargs)
                saved = True
            notification_queries.create_commission_created_notification_for_author(
                self)
            pass

        if not saved:
            super().save(*args, **kwargs)
            saved = True

    def should_notify_new_commission(self):
        should_notify = self.tracker.previous(
            "id") is None and not self.is_self_managed()
        return should_notify

    def friendly_state(self) -> str:
        COMMISSION_STATE_TO_FRIENDLY = dict(self.__class__.STATE_CHOICES)
        return COMMISSION_STATE_TO_FRIENDLY[self.state]

    def should_notify_state_change(self) -> bool:
        return (
            self.tracker.previous("state") is not None
            and self.tracker.has_changed("state")
            and not self.is_self_managed()
        )

    def post_clean_new_object(self):
        furfolio_validators.check_commission_meets_offer_max_review_commissions(
            self)
        furfolio_validators.check_commission_is_not_created_on_closed_offer(
            self)
        furfolio_validators.check_user_is_within_commission_limit_for_offer(
            self)

        if not self.is_self_managed():
            furfolio_validators.check_user_is_not_spamming_commissions(
                self.commissioner
            )

    def __str__(self):
        state_as_dict = dict(self.STATE_CHOICES)
        human_readable_state = state_as_dict[self.state]
        return f"({human_readable_state}) {self.commissioner.username} wants \"{self.offer.name}\" by {self.offer.author.username}"

    def get_absolute_url(self):
        return reverse("commission_detail", kwargs={"pk": self.pk})

    def is_active(self):
        return self.state in {
            Commission.STATE_ACCEPTED,
            Commission.STATE_IN_PROGRESS,
            Commission.STATE_CLOSED}

    def is_self_managed(self):
        return self.commissioner == self.offer.author

    def get_chat(self):
        return chat_queries.get_commission_chat_by_commission(self)
