from PIL import Image
import PIL.ImageFile
from io import BytesIO
from pathlib import Path
from model_utils import FieldTracker
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.indexes import GinIndex
from django.core import validators
from django.core.files import File
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from datetime import timedelta
import math

from . import validators as furfolio_validators
from . import mixins
from .queries import commissions as commission_queries
from .queries import users as user_queries
from .queries import offers as offer_queries
from .queries import notifications as notification_queries
from .email import send_commission_state_changed_email, send_new_offer_email, send_new_commission_email


PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True


AVERAGE_CHARACTERS_PER_WORD = 4.7


def remove_transparency(im, bg_colour=(255, 255, 255)):

    # Only process if image has transparency
    # (http://stackoverflow.com/a/1963146)
    if im.mode in ('RGBA', 'LA') or (
            im.mode == 'P' and 'transparency' in im.info):

        # Need to convert to RGBA if LA format due to a bug in PIL
        # (http://stackoverflow.com/a/1963146)
        alpha = im.convert('RGBA').split()[-1]

        # Create a new background image of our matt color.
        # Must be RGBA because paste requires both images have the same format
        # (http://stackoverflow.com/a/8720632  and  http://stackoverflow.com/a/9459208)
        bg = Image.new("RGBA", im.size, bg_colour + (255,))
        bg.paste(im, mask=alpha)
        return bg

    else:
        return im


def image_resize(image, width, height, transparency_remove=True,
                 fit_in_center=False):
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
        # Save the new resized file as usual, which will save to S3 using
        # django-storages
        image.save(img_filename, file_object)


class User(mixins.GetFullUrlMixin, AbstractUser):
    MAX_PROFILE_LENGTH = math.ceil(AVERAGE_CHARACTERS_PER_WORD * 1000)

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
        help_text="Avatars are optional. Your avatar will be resized to 64 by 64 pixels.",
        validators=[
            furfolio_validators.validate_profile_image_is_right_size,
            furfolio_validators.validate_avatar_has_max_size,
        ])
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
    profile = models.TextField(
        name="profile",
        verbose_name="Profile Description",
        max_length=MAX_PROFILE_LENGTH,
        blank=True,
        help_text="This will display on you profile page. Use this to describe yourself."
    )

    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    tracker = FieldTracker()

    class Meta:
        indexes = [
            GinIndex(fields=["username",], fastupdate=False,
                     name="user_username_index")
        ]

    def save(self, *args, **kwargs) -> None:
        if self.avatar and self.tracker.has_changed("avatar"):
            image_resize(
                self.avatar,
                User.AVATAR_SIZE_PIXELS[0],
                User.AVATAR_SIZE_PIXELS[1],
                transparency_remove=True,
                fit_in_center=True)
        super(User, self).save(*args, **kwargs)

    def get_following_users(self):
        return user_queries.get_users_following_user(self)

    def get_followed_users(self):
        return user_queries.get_followed_users(self)

    def get_absolute_url(self):
        return reverse("user", kwargs={"username": self.username})

    def can_commission_offer(self, offer: 'Offer'):
        if self == offer.author:
            return True
        elif offer.is_closed():
            return False
        elif offer.has_max_review_commissions():
            return False
        elif commission_queries.get_commissions_for_commissioner_and_offer(self, offer).count() >= offer.max_commissions_per_user:
            return False
        else:
            return True


class UserFollowingUser(models.Model):
    follower = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower")
    followed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followed")

    def __str__(self):
        return f"{self.follower.username} is following {self.followed.username}"


def seven_days_from_now():
    return timezone.now() + timedelta(days=7)


# limit offer description to about 1000 words
OFFER_DESCRIPTION_MAX_LENGTH = math.ceil(AVERAGE_CHARACTERS_PER_WORD * 1000)
# offer description must have at least about 4 words
OFFER_DESCRIPTION_MIN_LENGTH = math.floor(AVERAGE_CHARACTERS_PER_WORD * 4)

RATING_GENERAL = "GEN"
RATING_ADULT = "ADL"
RATING_TO_CHOICES = [
    (RATING_GENERAL, "General"),
    (RATING_ADULT, "Adult"),
]


class Offer(mixins.GetFullUrlMixin, models.Model):
    # https://en.wikipedia.org/wiki/ISO_4217#Active_codes_(List_One)
    EURO_SYMBOL = "\u20AC"
    CURRENCY_USD = "USD"
    CURRENCY_EUR = "EUR"
    CURRENCY_CHOICES = [
        (CURRENCY_USD, "$ United States Dollar (USD)"),
        (CURRENCY_EUR, EURO_SYMBOL + " Euro (EUR)"),
    ]

    HIGHEST_PRICE = 1_000_000_000

    ASPECT_RATIO_MIN = (1, 3)
    ASPECT_RATIO_MAX = (4, 1)
    THUMBNAIL_MAX_DIMENTIONS = (600, 350)

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
                Offer.THUMBNAIL_MAX_DIMENTIONS[0],
                Offer.THUMBNAIL_MAX_DIMENTIONS[1])

        # determine who to notify if offer is created
        if self.tracker.previous("id") is None:
            super(Offer, self).save(*args, **kwargs)
            notification_queries.create_offer_posted_notifications_for_followers(
                self)
        else:
            super(Offer, self).save(*args, **kwargs)

    def clean(self):
        furfolio_validators.validate_price_min_is_less_than_max(
            self.min_price, self.max_price)
        furfolio_validators.check_user_will_not_go_over_max_active_offers(
            self)
        furfolio_validators.validate_max_commissions_per_user_is_lte_to_max_review_commissions(
            self)

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
    chat = models.ForeignKey(
        "Chat",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    tracker = FieldTracker()

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def save(self, *args, **kwargs) -> None:
        saved: bool = False
        if self.should_notify_state_change():
            send_commission_state_changed_email(self)
        if self.should_notify_new_commission():
            if not saved:
                super().save(*args, **kwargs)
                saved = True
            send_new_commission_email(self)

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

    def clean(self) -> None:
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
        return super().clean()

    def __str__(self):
        return "Id: %i. \"%s\" requested \"%s\"." % (
            self.id, self.commissioner.username, self.offer.name)

    def get_absolute_url(self):
        return reverse("commission_detail", kwargs={"pk": self.pk})

    def is_active(self):
        return self.state in {
            Commission.STATE_ACCEPTED,
            Commission.STATE_IN_PROGRESS,
            Commission.STATE_CLOSED}

    def is_self_managed(self):
        return self.commissioner == self.offer.author


class TagCategory(models.Model):
    DESCRIPTION_MAX_LENGTH = math.ceil(
        AVERAGE_CHARACTERS_PER_WORD * 1000)

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
        AVERAGE_CHARACTERS_PER_WORD * 1000)

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


class Chat(models.Model):
    name = models.CharField(
        max_length=160,
        name="name",
        help_text="The name of the chat room.",
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return self.name


class ChatParticipant(models.Model):
    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
    )
    participant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return f"\"{self.participant}\" in chat \"{self.chat}\""


class ChatMessage(models.Model):

    MESSAGE_MAX_LENGTH = math.ceil(
        AVERAGE_CHARACTERS_PER_WORD * 350)

    chat = models.ForeignKey(
        Chat,
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    message = models.TextField(
        name="message",
        max_length=MESSAGE_MAX_LENGTH,
    )
    attachment = models.FileField(
        name="attachment",
        blank=True,
        validators=[
            furfolio_validators.validate_commission_message_attachment_has_max_size,
        ]
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)
    updated_date = models.DateTimeField(name="updated_date", auto_now=True)

    def __str__(self):
        return f"\"{self.author}\" made message in \"{self.chat}\""

    def get_html_id(self) -> str:
        return "message_" + str(self.pk)

    def get_absolute_url(self):
        return reverse("chat", kwargs={
                       "pk": self.chat.pk}) + "#" + self.get_html_id()

    def clean(self) -> None:
        furfolio_validators.validate_chat_message_author_is_participant(self)
        return super().clean()

    def save(self, *args, **kwargs):
        # if message is new, notify all recipients
        if not self.pk:
            save_return = super().save(*args, **kwargs)
            notification_queries.create_message_notifications_for_recipients(
                self)
            return save_return
        else:
            return super().save(*args, **kwargs)


class Notification(mixins.GetFullUrlMixin, models.Model):
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    seen = models.BooleanField(
        default=False,
    )

    created_date = models.DateTimeField(name="created_date", auto_now_add=True)

    def __str__(self):
        return f"\"{self.recipient}\" has a notification"

    def get_absolute_url(self):
        return reverse("open_notification", kwargs={"pk": self.pk})

    def get_content_url(self) -> str | None:
        """
        Returns the url that this notification points to.
        This url points to the content it is representing.
        This url does not "open" the notification.
        """
        if hasattr(self, "chatmessagenotification"):
            return self.chatmessagenotification.message.get_absolute_url()
        elif hasattr(self, "offerpostednotification"):
            return self.offerpostednotification.offer.get_absolute_url()
        else:
            return None


class ChatMessageNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    message = models.ForeignKey(
        ChatMessage,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"\"{self.notification.recipient}\" has a chat message notification"


class OfferPostedNotification(models.Model):
    notification = models.OneToOneField(
        Notification,
        on_delete=models.CASCADE,
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"\"{self.notification.recipient}\" has been notified of a new offer \"{self.offer.name}\""
