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


# limit offer description to about 1000 words
OFFER_DESCRIPTION_MAX_LENGTH = math.ceil(
    settings.AVERAGE_CHARACTERS_PER_WORD * 1000)
# offer description must have at least about 4 words
OFFER_DESCRIPTION_MIN_LENGTH = math.floor(
    settings.AVERAGE_CHARACTERS_PER_WORD * 4)


class Offer(mixins.CleaningMixin, mixins.GetFullUrlMixin, models.Model):
    # https://en.wikipedia.org/wiki/ISO_4217#Active_codes_(List_One)
    EURO_SYMBOL = "\u20AC"
    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_CHOICES = [
        (CURRENCY_USD, "$ United States Dollar (USD)"),
        (CURRENCY_EUR, EURO_SYMBOL + " Euro (EUR)"),
    ]

    HIGHEST_PRICE = 1_000_000_000
    MAX_ACTIVE_OFFERS_PER_USER = 3

    ASPECT_RATIO_MIN = (1, 3)
    ASPECT_RATIO_MAX = (4, 1)
    THUMBNAIL_MAX_DIMENSIONS = (1200, 700)

    SORT_RELEVANCE = "relevance"
    SORT_CREATED_DATE = "created_date"
    SORT_UPDATED_DATE = "updated_date"
    SORT_CHOICES = [
        (SORT_RELEVANCE, "Relevance"),
        (SORT_CREATED_DATE, "Created Date"),
        (SORT_UPDATED_DATE, "Updated Date"),
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
        help_text=mark_safe(
            """
            Describes the details of the offer.
            <br>
            Explain (when applicable):
            <ul>
                <li>
                    what service is being provided
                </li>
                <li>
                    what you need from the buyer (requirements, references, etc.)
                </li>
                <li>
                    when a commission is considered finished
                </li>
            </ul>
            """
        ),
        validators=[validators.MinLengthValidator(
            OFFER_DESCRIPTION_MIN_LENGTH),],
        default="",
    )
    cutoff_date = models.DateTimeField(
        name="cutoff_date",
        verbose_name="Cutoff Time",
        default=seven_days_from_now,
        help_text=mark_safe(
            """
            When your offer is no longer accepting commissions.
            <br>
            <span class="text-danger">Note</span>: This cannot be changed after the offer is created.
            """
        ),
        validators=[],
    )
    forced_closed = models.BooleanField(
        name="forced_closed",
        help_text="Indicates that the offer is closed, regardless if the cutoff date has passed or not.",
        default=False,
    )
    thumbnail = models.ImageField(
        name="thumbnail",
        blank=True,
        null=True,
        help_text="A thumbnail is optional, but it will be shown when users search for offers and when they visit this offer's page.",
        validators=[
            furfolio_validators.validate_offer_thumbnail_aspect_ratio,
            furfolio_validators.validate_offer_thumbnail_has_max_size,
        ])
    rating = models.CharField(
        name="rating",
        max_length=3,
        choices=RATING_TO_CHOICES,
        default=RATING_GENERAL,
    )
    slots = models.PositiveIntegerField(
        name="slots",
        verbose_name="Slots",
        help_text=mark_safe(
            """
            The maximum number of commissions you are willing to work on for this offer.
            <br>
            This is not a hard limit; it is used to communicate how many commissions you are willing to work.
            """
        ),
        validators=[
            validators.MinValueValidator(1),
        ],
        default=3,
    )
    max_review_commissions = models.PositiveIntegerField(
        name="max_review_commissions",
        verbose_name="Maximum Commissions in Review",
        help_text=mark_safe(
            """
            The maximum number of commissions allowed to be in the review state.
            <br>
            Use this to prevent being overloaded with too many commission requests at a time for this offer.
            <br>
            Self-managed commissions are not limited by this, but contribute to the number of commissions in review.
            """
        ),
        validators=[
            validators.MinValueValidator(1),
        ],
        default=5,
    )
    min_price = models.PositiveIntegerField(
        name="min_price",
        verbose_name="Minimum Price",
        help_text="The minimum price for commissions of this offer.",
        default=0,
        validators=[
            validators.MaxValueValidator(HIGHEST_PRICE - 1)
        ]
    )
    max_price = models.PositiveIntegerField(
        name="max_price",
        verbose_name="Maximum Price",
        help_text="The maximum price for commissions of this offer.",
        default=5,
        validators=[
            validators.MinValueValidator(1),
            validators.MaxValueValidator(HIGHEST_PRICE)
        ]
    )
    currency = models.CharField(
        name="currency",
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_USD,
    )
    max_commissions_per_user = models.PositiveIntegerField(
        name="max_commissions_per_user",
        verbose_name="Maximum Commissions per User",
        help_text=mark_safe(
            """
            Limits how many commissions a user can make on this offer.
            <br>
            Commission state does not matter, so if you reject a commission from a user, it still counts to this limit.
            <br>
            Self-managed commissions are not limited.
            """
        ),
        default=1,
        validators=[
            validators.MinValueValidator(1),
        ],
    )

    tracker = FieldTracker()

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    class Meta:
        indexes = [
            GinIndex(fields=["name", "description"],
                     fastupdate=False, name="offer_name_description_index"),
        ]

    def __str__(self):
        return "Id: %i. \"%s\" by %s." % (
            self.id, self.name, self.author.username)

    def save(self, *args, **kwargs) -> None:
        if self.thumbnail and self.tracker.has_changed("thumbnail"):
            image_resize(
                self.thumbnail,
                Offer.THUMBNAIL_MAX_DIMENSIONS[0],
                Offer.THUMBNAIL_MAX_DIMENSIONS[1])

        # determine who to notify if offer is created
        if self.tracker.previous("id") is None:
            super(Offer, self).save(*args, **kwargs)
            notification_queries.create_offer_posted_notifications_for_followers(
                self)
        else:
            super(Offer, self).save(*args, **kwargs)

    def clean(self):
        super().clean()
        furfolio_validators.validate_price_min_is_less_than_max(
            self.min_price, self.max_price)
        furfolio_validators.validate_max_commissions_per_user_is_lte_to_max_review_commissions(
            self)

    def post_clean_new_object(self):
        furfolio_validators.check_user_will_not_go_over_max_active_offers(
            self, self.MAX_ACTIVE_OFFERS_PER_USER)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})

    def get_active_commissions(self):
        return commission_queries.get_active_commissions_of_offer(self)

    def get_commissions_in_review(self):
        return commission_queries.get_commissions_in_review_for_offer(self)

    def is_closed(self):
        if self.forced_closed:
            return True
        elif self.cutoff_date < timezone.now():
            return True
        return False

    def has_max_review_commissions(self) -> bool:
        num_commissions_in_review = self.get_commissions_in_review().count()
        return num_commissions_in_review >= self.max_review_commissions

    def get_who_to_notify_for_new_offer(self):
        return offer_queries.get_who_to_notify_for_new_offer(self)

    def get_currency_symbol(self) -> str:
        match self.currency:
            case self.__class__.CURRENCY_USD:
                return "$"
            case self.__class__.CURRENCY_EUR:
                return self.__class__.EURO_SYMBOL

    def get_iso_4217_currency_code(self) -> str:
        match self.currency:
            case self.__class__.CURRENCY_USD:
                return "USD"
            case self.__class__.CURRENCY_EUR:
                return "EUR"

    def get_rating_friendly(self) -> str:
        rating_to_human_friendly = dict(RATING_TO_CHOICES)
        return rating_to_human_friendly[self.rating]

    def is_adult(self) -> bool:
        return self.rating == RATING_ADULT

    class SlotInfo:
        def __init__(self, max_slots: int, slots_taken: int):
            self.max_slots = max_slots
            self.slots_taken = slots_taken

        def get_capped_slots_taken(self) -> int:
            return min(self.max_slots, self.slots_taken)

        def is_more_taken_than_max(self) -> bool:
            return self.slots_taken > self.max_slots

    def get_slot_info(self) -> SlotInfo:
        slots_taken = self.get_active_commissions().count()
        return self.__class__.SlotInfo(self.slots, slots_taken)


class OfferDescriptiveStrForCreator(Offer):
    class Meta:
        proxy = True

    def __str__(self):
        string = f"{self.name}"
        if self.is_closed():
            string = string + " (Closed)"
        return string
