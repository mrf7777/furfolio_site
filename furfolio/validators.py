from datetime import datetime, timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_datetime_not_in_past(value: datetime):
    current_datetime = timezone.now()
    if value < current_datetime:
        raise ValidationError("Provided date-time must not be in the past.")


def validate_datetime_at_least_12_hours(value: datetime):
    future_12_hours = timezone.now() + timedelta(hours=12)
    if value < future_12_hours:
        raise ValidationError(
            "Provided date-time must be at least 12 hours into the future.")
