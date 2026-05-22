import re

from django.core.exceptions import ValidationError

PHONE_REGEX = re.compile(r'^\+?[\d\s\-()]{10,15}$')


def validate_phone(value):
    if not PHONE_REGEX.match(value):
        raise ValidationError('Enter a valid phone number (10–15 digits).')


def validate_reject_reason(value):
    if len(value.strip()) < 10:
        raise ValidationError('Rejection reason must be at least 10 characters.')
