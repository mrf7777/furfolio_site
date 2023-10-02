from cgitb import text
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core import validators
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
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
    
    class Meta:
        indexes = [
            GinIndex(fields=["username",], fastupdate=False, name="user_username_index")
        ]

    def full_text_search_creators(text_query: str):
        text_query_cleaned = text_query.strip()
        search_vector = SearchVector("username", weight="A")
        search_query = SearchQuery(text_query_cleaned)
        search_rank = SearchRank(search_vector, search_query)
        return User.objects.filter(role=User.ROLE_CREATOR).annotate(rank=search_rank).filter(rank__gte=0.2).order_by("-rank")
        
    def get_creators():
        return User.objects.filter(role=User.ROLE_CREATOR)

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
    # TODO: what is the value added by this field? Simply keep the review commissions limit and reject requests after offer cutoff date.
    slots = models.PositiveIntegerField(
        name="slots",
        verbose_name="Slots",
        help_text=mark_safe("The maximum number of commissions you are willing to work on for this offer.<br>This is not a hard limit; it is used to communicate how many commissions you are willing to work."),
        validators=[
            validators.MinValueValidator(1),
        ],
        default=3,
    )
    max_review_commissions = models.PositiveIntegerField(
        name="max_review_commissions",
        verbose_name="Max Commissions in Review",
        help_text=mark_safe("The maximum number of commissions allowed to be in the review state.<br>Use this to prevent being overloaded with too many commission requests at a time."),
        validators=[
            validators.MinValueValidator(1),
        ],
        default=5,
    )
    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=["name", "description"], fastupdate=False, name="offer_name_description_index"),
        ]

    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})
    
    def get_active_commissions(self):
        return Commission.get_active_commissions().filter(offer__pk=self.pk)
    
    def get_commissions_in_review(self):
        return Commission.objects.filter(offer__pk=self.pk, state=Commission.STATE_REVIEW)

    def full_text_search_offers(text_query: str):
        text_query_cleaned = text_query.strip()
        search_vector = SearchVector("name", weight="A") + SearchVector("description", weight="A")
        search_query = SearchQuery(text_query_cleaned)
        search_rank = SearchRank(search_vector, search_query)
        return Offer.objects.annotate(rank=search_rank).filter(rank__gte=0.2).order_by("-rank")

    def is_closed(self):
        if self.forced_closed:
            return True
        elif self.cutoff_date < timezone.now():
            return True
        return False
    
    def is_full(self):
        num_commissions_in_review = self.get_commissions_in_review().count()
        num_active_commissions = self.get_active_commissions().count()
        if num_active_commissions >= self.slots:
            return True
        elif num_commissions_in_review >= self.max_review_commissions:
            return True
        else:
            return False


# limit initial request text to about 800 words
COMMISSION_INITIAL_REQUEST_TEXT_MAX_LENGTH = math.ceil(
    AVERAGE_CHARACTERS_PER_WORD * 800)


class Commission(models.Model):
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

    def clean(self) -> None:
        furfolio_validators.check_commission_meets_offer_max_review_commissions(self, self.offer)
        return super().clean()

    def __str__(self):
        return "Id: %i. \"%s\" requested \"%s\"." % (self.id, self.commissioner.username, self.offer.name)

    def get_absolute_url(self):
        return reverse("commission_detail", kwargs={"pk": self.pk})
    
    def get_active_commissions():
        query = Q(
            state=Commission.STATE_ACCEPTED
        ) | Q(
            state=Commission.STATE_IN_PROGRESS
        ) | Q(
            state=Commission.STATE_CLOSED
        )
        return Commission.objects.filter(Q(state=Commission.STATE_ACCEPTED) | Q(state=Commission.STATE_IN_PROGRESS) | Q(state=Commission.STATE_CLOSED))

    def is_active(self):
        return self.state in {Commission.STATE_ACCEPTED, Commission.STATE_IN_PROGRESS, Commission.STATE_CLOSED}

# limit commisson message to about 350 words
COMMISSION_MESSAGE_MAX_LENGTH = math.ceil(
    AVERAGE_CHARACTERS_PER_WORD * 350)


class CommissionMessage(models.Model):
    commission = models.ForeignKey(
        Commission,
        name="commission",
        on_delete=models.CASCADE,
    )
    # if the author is deleted, keep the chat history by preserving these messages
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
    )
    message = models.TextField(
        name="message",
        max_length=COMMISSION_MESSAGE_MAX_LENGTH,
    )
    attachment = models.FileField(
        name="attachment",
        blank=True,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def been_edited(self) -> bool:
        # only consider to be edited if change to message happened 10 seconds after being created
        return abs((self.created_date - self.updated_date).total_seconds()) > 10

    def get_html_id(self) -> str:
        return "message_" + str(self.pk)

    def get_absolute_url(self):
        return reverse("commission_chat", kwargs={"pk": self.commission.pk}) + "#" + self.get_html_id()
