from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models.fields.files import ImageFieldFile, FileField
from django.utils.safestring import mark_safe
from . import models
from .queries import commissions as commission_queries
from .queries import offers as offer_queries


def validate_datetime_not_in_past(value: datetime):
    current_datetime = timezone.now()
    if value < current_datetime:
        raise ValidationError("Provided date-time must not be in the past.")


def validate_datetime_is_not_over_year_into_future(value: datetime):
    current_datetime = timezone.now()
    year_into_future = current_datetime + timedelta(days=365)
    if value > year_into_future:
        raise ValidationError(
            "Provided date-time must not be over a year into the future.")


def validate_datetime_at_least_12_hours(value: datetime):
    future_12_hours = timezone.now() + timedelta(hours=12)
    if value < future_12_hours:
        raise ValidationError(
            "Provided date-time must be at least 12 hours into the future.")


def validate_profile_image_is_right_size(value: ImageFieldFile):
    AVATAR_MIN_WIDTH = models.User.AVATAR_SIZE_PIXELS[0]
    AVATAR_MIN_HEIGHT = models.User.AVATAR_SIZE_PIXELS[1]
    if value.height < AVATAR_MIN_HEIGHT or value.width < AVATAR_MIN_WIDTH:
        raise ValidationError(
            f"Avatar width and height must be at least {AVATAR_MIN_WIDTH} and {AVATAR_MIN_HEIGHT} pixels respectively")


def validate_offer_thumbnail_aspect_ratio(value: ImageFieldFile):
    ASPECT_RATIO_MIN_NUMBER = models.Offer.ASPECT_RATIO_MIN[0] / \
        models.Offer.ASPECT_RATIO_MIN[1]
    ASPECT_RATIO_MAX_NUMBER = models.Offer.ASPECT_RATIO_MAX[0] / \
        models.Offer.ASPECT_RATIO_MAX[1]
    thumbnail_aspect_ratio_number = value.width / value.height
    if thumbnail_aspect_ratio_number < ASPECT_RATIO_MIN_NUMBER:
        raise ValidationError(
            f"The aspect ratio of the image is too small. Try an image that has less height.")
    if thumbnail_aspect_ratio_number > ASPECT_RATIO_MAX_NUMBER:
        raise ValidationError(
            f"The aspect ratio of the image is too large. Try an image that has less width.")


def validate_price_min_is_less_than_max(min_price: int, max_price: int):
    if max_price <= min_price:
        example_valid_max_price = min_price + 1
        raise ValidationError(
            "Maximum price must be greater than the minimum price. Maybe try a maximum price of " +
            str(example_valid_max_price) + "."
        )


def check_commission_meets_offer_max_review_commissions(commission: 'models.Commission'):
    if commission.is_self_managed():
        return

    num_offer_commissions_in_review_state = commission.offer.get_commissions_in_review().count()
    if num_offer_commissions_in_review_state >= commission.offer.max_review_commissions:
        raise ValidationError(
            "Commission is not valid because the offer has max number of commissions in review state.")


def check_user_is_within_commission_limit_for_offer(commission: 'models.Commission'):
    # self-managed commissions are exempt from this check
    if commission.is_self_managed():
        return

    num_commissions_for_commissioner_and_offer = commission_queries.get_commissions_for_commissioner_and_offer(
        commission.commissioner,
        commission.offer
    ).count()
    if num_commissions_for_commissioner_and_offer >= commission.offer.max_commissions_per_user:
        raise ValidationError(
            "Commission cannot be created since you would excede the limit configured for this offer."
        )


def validate_max_commissions_per_user_is_lte_to_max_review_commissions(offer: 'models.Offer'):
    if offer.max_commissions_per_user > offer.max_review_commissions:
        raise ValidationError(
            mark_safe(
                f"""
                Maximum Commissions per User cannot be greater than Maximum Commissions in Review.<br>
                Try setting Maximum Commissions per User to {offer.max_review_commissions}.
                """
            )
        )


def check_user_is_not_spamming_offers(user: 'models.User'):
    OFFER_CREATION_COOLDOWN = 60
    try:
        latest_offer_by_user = models.Offer.objects.filter(
            author=user).latest("created_date")
        current_time = timezone.now()
        difference_in_seconds = (
            current_time - latest_offer_by_user.created_date
        ).total_seconds()
        if difference_in_seconds < OFFER_CREATION_COOLDOWN:
            raise ValidationError(
                "Offer is too recent. Please wait before trying again."
            )
    except ObjectDoesNotExist:
        pass


def check_commission_is_not_created_on_closed_offer(commission: 'models.Commission'):
    # self-managed commissions are exempt and can be created on closed offers
    if commission.is_self_managed():
        return

    if commission.offer.is_closed():
        raise ValidationError(
            "Commission cannot be created on a closed offer unless you are the offer author."
        )


def check_user_is_not_spamming_commissions(user: 'models.User'):
    COMMISSION_CREATION_COOLDOWN = 30
    try:
        latest_commission_by_user = models.Commission.objects.filter(
            commissioner=user).latest("created_date")
        current_time = timezone.now()
        difference_in_seconds = (
            current_time - latest_commission_by_user.created_date
        ).total_seconds()
        if difference_in_seconds < COMMISSION_CREATION_COOLDOWN:
            raise ValidationError(
                "Commission is too recent. Please wait before trying again."
            )
    except ObjectDoesNotExist:
        pass


def check_user_is_not_spamming_commission_messages(user: 'models.User'):
    COMMISSION_MESSAGE_CREATION_COOLDOWN = 7
    try:
        latest_commission_message_by_user = models.CommissionMessage.objects.filter(
            author=user).latest("created_date")
        current_time = timezone.now()
        difference_in_seconds = (
            current_time - latest_commission_message_by_user.created_date
        ).total_seconds()
        if difference_in_seconds < COMMISSION_MESSAGE_CREATION_COOLDOWN:
            raise ValidationError(
                "Message is too recent. Please wait before trying again."
            )
    except ObjectDoesNotExist:
        pass


def check_file_field_has_max_size(file_field: FileField, max_file_size: int):
    if file_field.size > max_file_size:
        raise ValidationError(
            "File size is too large."
        )


def validate_avatar_has_max_size(value: FileField):
    MAX_AVATAR_FILE_SIZE = 5 * 1024 * 1024  # 5 MiB
    check_file_field_has_max_size(value, MAX_AVATAR_FILE_SIZE)


def validate_offer_thumbnail_has_max_size(value: FileField):
    MAX_OFFER_THUMBNAIL_FILE_SIZE = 25 * 1024 * 1024    # 25 MiB
    check_file_field_has_max_size(value, MAX_OFFER_THUMBNAIL_FILE_SIZE)


def validate_commission_attachment_has_max_size(value: FileField):
    MAX_COMMISSION_ATTACHMENT_FILE_SIZE = 25 * 1024 * 1024  # 25 MiB
    check_file_field_has_max_size(value, MAX_COMMISSION_ATTACHMENT_FILE_SIZE)


def validate_commission_message_attachment_has_max_size(value: FileField):
    MAX_COMMISSION_MESSAGE_ATTACHMENT_FILE_SIZE = 10 * 1024 * 1024  # 10 MiB
    check_file_field_has_max_size(
        value, MAX_COMMISSION_MESSAGE_ATTACHMENT_FILE_SIZE)


def check_user_will_not_go_over_max_active_offers(offer: 'models.Offer'):
    MAX_ACTIVE_OFFERS_PER_USER = 5
    # a closed offer should not count
    if offer.is_closed():
        return

    # offer is active, so ensure it is under the limit
    active_offers_by_author = offer_queries.get_active_offers_for_user(
        offer.author)
    if active_offers_by_author.count() >= MAX_ACTIVE_OFFERS_PER_USER:
        raise ValidationError(
            f"Cannot save offer because the number of active offers is at its maximum limit (which is {MAX_ACTIVE_OFFERS_PER_USER}). Consider force-closing an active offer or waiting for an offer to pass its cutoff date."
        )
