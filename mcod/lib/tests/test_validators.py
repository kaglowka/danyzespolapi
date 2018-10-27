import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password, get_default_password_validators
from django.core.exceptions import ValidationError


@pytest.mark.run(order=0)
def test_invalid_passwords(invalid_passwords_with_user):
    u = get_user_model()(email='aaa@bbb.cc', fullname='Test User')
    for password in invalid_passwords_with_user:
        with pytest.raises(ValidationError):
            validate_password(password, user=u)


@pytest.mark.run(order=0)
def test_valid_passwords(valid_passwords):
    u = get_user_model()(email='aaa@bbb.cc', fullname='Test User')
    for password in valid_passwords:
        assert validate_password(password, user=u) is None


@pytest.mark.run(order=0)
def test_password_validators_help_text():
    validators = get_default_password_validators()
    for validator in validators:
        assert len(validator.get_help_text()) > 0
