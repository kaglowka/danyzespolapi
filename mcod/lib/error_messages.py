from django.utils.translation import gettext as _

email_error_messages = {
    'invalid': _('Not a valid email address.')
}

str_error_messages = {
    'invalid': _('Not a valid string.'),
    'invalid_utf8': _('Not a valid utf-8 string.')
}

number_error_messages = {
    'invalid': _('Not a valid number.')
}

int_error_messages = {
    'invalid': _('Not a valid integer.')
}

decimal_error_messages = {
    'special': _('Special numeric values are not permitted.')
}

boolean_error_messages = {
    'invalid': _('Not a valid boolean.')
}

datetime_error_messages = {
    'invalid': _('Not a valid datetime.'),
    'format': _('"{input}" cannot be formatted as a datetime.')
}

time_error_messages = {
    'invalid': _('Not a valid time.'),
    'format': _('"{input}" cannot be formatted as a time.'),
}

date_error_messages = {
    'invalid': _('Not a valid date.'),
    'format': _('"{input}" cannot be formatted as a date.'),
}

url_error_messages = {
    'invalid': _('Not a valid URL.')
}
