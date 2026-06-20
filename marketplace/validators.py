from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

def flexible_password_validator(value):
    """
    Allow any password as long as it's at least 4 characters long.
    No complexity requirements.
    """
    if len(value) < 4:
        raise ValidationError(
            _('Password must be at least 4 characters long.'),
            code='password_too_short',
        )
    # No other validation - users can use numbers only, words, etc.