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
    AVATAR_WIDTH_HEIGHT = 64
    if value.height != AVATAR_WIDTH_HEIGHT or value.width != AVATAR_WIDTH_HEIGHT:
        raise ValidationError("Avatar must be 64 by 64 pixels.")


def check_commission_meets_offer_max_review_commissions(commission, offer):
    num_offer_commissions_in_review_state = models.Commission.objects.filter(
        offer__pk=offer.pk, state=models.Commission.STATE_REVIEW).count()
    if num_offer_commissions_in_review_state >= offer.max_review_commissions:
        raise ValidationError(
            "Commission is not valid because the offer has max number of commissions in review state.")
