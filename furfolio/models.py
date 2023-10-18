from functools import reduce
from locale import currency
from tabnanny import verbose
from PIL import Image
import PIL.ImageFile
from io import BytesIO
from pathlib import Path
from model_utils import FieldTracker
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core import validators
from django.core.files import File
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import math

from furfolio import form_fields
from . import validators as furfolio_validators
from . import mixins
from . import form_fields
from .queries import commissions as commission_queries
from .email import send_commission_state_changed_email, send_new_commission_message_email


PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True


AVERAGE_CHARACTERS_PER_WORD = 4.7


def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im


def image_resize(image, width, height, transparency_remove=True, fit_in_center=False):
    """
    https://blog.soards.me/posts/resize-image-on-save-in-django-before-sending-to-amazon-s3/
    """

    # Open the image using Pillow
    img = Image.open(image)
    img = img.convert("RGBA")
    # check if either the width or height is greater than the max
    if img.width > width or img.height > height:
        output_size = (width, height)
        # Create a new resized “thumbnail” version of the image with Pillow
        img.thumbnail(output_size)
        if fit_in_center:
            new_image = Image.new(
                "RGBA",
                (width, height),
                (255, 255, 255),
            )
            new_image.paste(
                img,
                ((width - img.width) // 2,
                 (height - img.height) // 2),
            )
            img = new_image
        if transparency_remove:
            img = remove_transparency(img)
        # Find the file name of the image
        img_filename = Path(image.file.name).name
        # Save the resized image into the buffer, noting the correct file type
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        # Wrap the buffer in File object
        file_object = File(buffer)
        # Save the new resized file as usual, which will save to S3 using django-storages
        image.save(img_filename, file_object)


class User(mixins.GetFullUrlMixin, AbstractUser):
    ROLE_BUYER = "BUYER"
    ROLE_CREATOR = "CREATOR"
    ROLE_CHOICES = [
        (ROLE_BUYER, "Buyer"),
        (ROLE_CREATOR, "Creator"),
    ]
    AVATAR_SIZE_PIXELS = (64, 64)
    avatar = models.ImageField(
        name="avatar",
        blank=True,
        help_text="Avatars are optional. Your avatar must be 64 by 64 pixels.",
        validators=[
            furfolio_validators.validate_profile_image_is_right_size,
            furfolio_validators.validate_avatar_has_max_size,
        ]
    )
    role = models.CharField(
        max_length=7,
        choices=ROLE_CHOICES,
        default=ROLE_BUYER,
        help_text="Your role on this platform. This is used to optimize your experience and to let others know how you want to use this website."
    )
    consent_to_adult_content = models.BooleanField(
        name="consent_to_adult_content",
        verbose_name="Consent to see adult content",
        help_text=mark_safe(
            "Indicate if you would like to see adult content on this website. If not indicated, you will not see adult content.<br> If you consent, you agree that you are legally allowed to view \"adult\" content."),
        default=False,
    )

    tracker = FieldTracker()

    class Meta:
        indexes = [
            GinIndex(fields=["username",], fastupdate=False,
                     name="user_username_index")
        ]

    def save(self, *args, **kwargs) -> None:
        if self.avatar and self.tracker.has_changed("avatar"):
            image_resize(
                self.avatar, User.AVATAR_SIZE_PIXELS[0], User.AVATAR_SIZE_PIXELS[1], transparency_remove=True, fit_in_center=True)
        super(User, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("user", kwargs={"username": self.username})


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)


# limit offer description to about 1000 words
OFFER_DESCRIPTION_MAX_LENGTH = math.ceil(AVERAGE_CHARACTERS_PER_WORD * 1000)
# offer description must have at least about 4 words
OFFER_DESCRIPTION_MIN_LENGTH = math.floor(AVERAGE_CHARACTERS_PER_WORD * 4)


class Offer(mixins.GetFullUrlMixin, models.Model):
    RATING_GENERAL = "GEN"
    RATING_ADULT = "ADL"
    RATING_TO_CHOICES = [
        (RATING_GENERAL, "General"),
        (RATING_ADULT, "Adult"),
    ]

    # https://en.wikipedia.org/wiki/ISO_4217#Active_codes_(List_One)
    EURO_SYMBOL = "\u20AC"
    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_CHOICES = [
        (CURRENCY_USD, "$ United States Dollar (USD)"),
        (CURRENCY_EUR, EURO_SYMBOL + " Euro (EUR)"),
    ]

    ASPECT_RATIO_MIN = (1, 3)
    ASPECT_RATIO_MAX = (4, 1)
    THUMBNAIL_MAX_DIMENTIONS = (600, 350)
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
            furfolio_validators.validate_datetime_is_not_over_year_into_future,
        ],
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
        validators=[
            furfolio_validators.validate_offer_thumbnail_aspect_ratio,
            furfolio_validators.validate_offer_thumbnail_has_max_size,
        ]
    )
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
            "The maximum number of commissions you are willing to work on for this offer.<br>This is not a hard limit; it is used to communicate how many commissions you are willing to work."),
        validators=[
            validators.MinValueValidator(1),
        ],
        default=3,
    )
    max_review_commissions = models.PositiveIntegerField(
        name="max_review_commissions",
        verbose_name="Max Commissions in Review",
        help_text=mark_safe(
            "The maximum number of commissions allowed to be in the review state.<br>Use this to prevent being overloaded with too many commission requests at a time for this offer."),
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
    )
    max_price = models.PositiveIntegerField(
        name="max_price",
        verbose_name="Maximum Price",
        help_text="The maximum price for commissions of this offer.",
        default=5,
        validators=[validators.MinValueValidator(1),]
    )
    currency = models.CharField(
        name="currency",
        max_length=3,
        choices=CURRENCY_CHOICES,
        default=CURRENCY_USD,
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
        return "Id: %i. \"%s\" by %s." % (self.id, self.name, self.author.username)

    def save(self, *args, **kwargs) -> None:
        if self.thumbnail and self.tracker.has_changed("thumbnail"):
            image_resize(
                self.thumbnail, Offer.THUMBNAIL_MAX_DIMENTIONS[0], Offer.THUMBNAIL_MAX_DIMENTIONS[1])
        super(Offer, self).save(*args, **kwargs)

    def clean(self):
        furfolio_validators.check_user_is_not_spamming_offers(self.author)
        furfolio_validators.validate_price_min_is_less_than_max(
            self.min_price, self.max_price)
        furfolio_validators.check_user_will_not_go_over_max_active_offers(
            self)

    def get_absolute_url(self):
        return reverse("offer_detail", kwargs={"pk": self.pk})

    def get_active_commissions(self):
        return commission_queries.get_active_commissions_of_offer(self)

    def get_commissions_in_review(self):
        return Commission.objects.filter(offer__pk=self.pk, state=Commission.STATE_REVIEW)

    def full_text_search_offers(text_query: str, author: str, sort: str, closed_offers: bool, consent_to_adult_content: bool):
        query = Offer.objects
        text_query_cleaned = text_query.strip()
        author_cleaned = author.strip()
        if text_query_cleaned:
            search_vector = SearchVector(
                "name", weight="A") + SearchVector("description", weight="A")
            search_query = SearchQuery(text_query_cleaned)
            search_rank = SearchRank(search_vector, search_query)
            query = query.annotate(rank=search_rank).filter(rank__gte=0.2)
        if author_cleaned:
            print("query:", query)
            query = query.filter(author__username=author_cleaned)
            print("query:", query)
        if not closed_offers:
            current_datetime = timezone.now()
            query = query.filter(
                cutoff_date__gt=current_datetime
            ).filter(
                forced_closed=False
            )
        if not consent_to_adult_content:
            query = query.filter(rating=Offer.RATING_GENERAL)
        match sort:
            case form_fields.SortField.CHOICE_RELEVANCE:
                if text_query_cleaned:
                    query = query.order_by("-rank")
                else:
                    query = query.order_by("-created_date")
            case form_fields.SortField.CHOICE_CREATED_DATE:
                query = query.order_by("-created_date")
            case form_fields.SortField.CHOICE_UPDATED_DATE:
                print("updated date")
                query = query.order_by("-updated_date")
            case _:
                query = query.order_by("-created_date")
        return query

    def is_closed(self):
        if self.forced_closed:
            return True
        elif self.cutoff_date < timezone.now():
            return True
        return False

    def has_max_review_commissions(self) -> bool:
        num_commissions_in_review = self.get_commissions_in_review().count()
        return num_commissions_in_review >= self.max_review_commissions

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

    def get_active_offers():
        current_time = timezone.now()
        return Offer.objects.filter(cutoff_date__gte=current_time, forced_closed=False)


class OfferDescriptiveStrForCreator(Offer):
    class Meta:
        proxy = True

    def __str__(self):
        string = f"{self.name}"
        if self.is_closed():
            string = string + " (Closed)"
        return string

    def get_offers_with_commission_in_review_accepted_or_in_progress_state():
        return OfferDescriptiveStrForCreator.objects.filter(
            Q(commission__state=Commission.STATE_REVIEW)
            | Q(commission__state=Commission.STATE_ACCEPTED)
            | Q(commission__state=Commission.STATE_IN_PROGRESS)
        ).distinct()


# limit initial request text to about 800 words
COMMISSION_INITIAL_REQUEST_TEXT_MAX_LENGTH = math.ceil(
    AVERAGE_CHARACTERS_PER_WORD * 800)


class Commission(mixins.GetFullUrlMixin, models.Model):
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
        if self.should_notify_state_change():
            send_commission_state_changed_email(self)
        super().save(*args, **kwargs)

    def friendly_state(self) -> str:
        COMMISSION_STATE_TO_FRIENDLY = dict(self.__class__.STATE_CHOICES)
        return COMMISSION_STATE_TO_FRIENDLY[self.state]

    def should_notify_state_change(self) -> bool:
        return (
            self.tracker.previous("state") is not None
            and self.tracker.has_changed("state")
            and not self.is_self_managed()
        )

    def clean(self) -> None:
        furfolio_validators.check_commission_meets_offer_max_review_commissions(
            self)
        furfolio_validators.check_commission_is_not_created_on_closed_offer(
            self)
        if not self.is_self_managed():
            furfolio_validators.check_user_is_not_spamming_commissions(
                self.commissioner
            )
        return super().clean()

    def __str__(self):
        return "Id: %i. \"%s\" requested \"%s\"." % (self.id, self.commissioner.username, self.offer.name)

    def get_absolute_url(self):
        return reverse("commission_detail", kwargs={"pk": self.pk})

    def is_active(self):
        return self.state in {Commission.STATE_ACCEPTED, Commission.STATE_IN_PROGRESS, Commission.STATE_CLOSED}

    def is_self_managed(self):
        return self.commissioner.pk == self.offer.author.pk


# limit commisson message to about 350 words
COMMISSION_MESSAGE_MAX_LENGTH = math.ceil(
    AVERAGE_CHARACTERS_PER_WORD * 350)


class CommissionMessage(mixins.GetFullUrlMixin, models.Model):
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
        validators=[
            furfolio_validators.validate_commission_message_attachment_has_max_size,
        ]
    )

    tracker = FieldTracker()

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if self.should_notify_new_message():
            send_new_commission_message_email(self)

    def clean(self) -> None:
        furfolio_validators.check_user_is_not_spamming_commission_messages(
            self.author)
        return super().clean()

    def should_notify_new_message(self):
        return (
            # if message is newly created
            self.tracker.previous("pk") is None
            and not self.commission.is_self_managed()   # and commission is not self managed
        )

    def been_edited(self) -> bool:
        # only consider to be edited if change to message happened 10 seconds after being created
        return abs((self.created_date - self.updated_date).total_seconds()) > 10

    def get_html_id(self) -> str:
        return "message_" + str(self.pk)

    def get_receiving_user(self) -> User | None:
        """
        Returns the user that is the recipient of this message.
        Because a chat always has two users, it returns the user
        that did NOT send this message.
        """
        if self.author is not None:
            if self.author.pk == self.commission.commissioner.pk:
                return self.commission.offer.author
            else:
                return self.commission.commissioner

    def get_absolute_url(self):
        return reverse("commission_chat", kwargs={"pk": self.commission.pk}) + "#" + self.get_html_id()
