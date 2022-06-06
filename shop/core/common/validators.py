import keyword
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


def non_python_keyword(value):
    if keyword.iskeyword(value):
        raise ValidationError(_("This field is invalid as its value is forbidden"))
    return value
