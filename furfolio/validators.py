from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError


def validate_datetime_not_in_past(value: datetime):
    current_datetime = timezone.now()
    if value < current_datetime:
        raise ValidationError("Provided date-time must not be in the past.")
