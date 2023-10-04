from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.fields.files import ImageFieldFile
from django.db.models.query import Q
from . import models


def validate_datetime_not_in_past(value: datetime):
    current_datetime = timezone.now()
    if value < current_datetime:
        raise ValidationError("Provided date-time must not be in the past.")


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
        models.Offer.ASPECT_RATIO_MIN[0]
    ASPECT_RATIO_MAX_NUMBER = models.Offer.ASPECT_RATIO_MAX[0] / \
        models.Offer.ASPECT_RATIO_MAX[0]
    thumbnail_aspect_ratio_number = value.width / value.height
    if thumbnail_aspect_ratio_number < ASPECT_RATIO_MIN_NUMBER:
        raise ValidationError(
            f"The aspect ratio of the image is too small. Try an image that has less height.")
    if thumbnail_aspect_ratio_number > ASPECT_RATIO_MAX_NUMBER:
        raise ValidationError(
            f"The aspect ratio of the image is too large. Try an image that has less width.")


def check_commission_meets_offer_max_review_commissions(offer):
    num_offer_commissions_in_review_state = models.Commission.objects.filter(
        offer__pk=offer.pk, state=models.Commission.STATE_REVIEW).count()
    if num_offer_commissions_in_review_state >= offer.max_review_commissions:
        raise ValidationError(
            "Commission is not valid because the offer has max number of commissions in review state.")
