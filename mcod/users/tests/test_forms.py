import pytest
# import json
from mcod.organizations.models import Organization

from mcod.users.forms import UserCreationForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'email, password1, password2, customfields, fullname, is_staff, is_superuser, state, validity',
    [
        (
                'rtest1@test.pl',
                'password',
                'password',
                '{"official_phone": "", "official_position": ""}',
                'R test',
                True,
                True,
                'active',
                True
        ),
        (
                'rtest1@test.pl', None, None, '{"official_phone": "", "official_position": ""}', 'R test', True, True,
                'active',
                False
        ),
        (
                None, 'password', 'password', '{"official_phone": "", "official_position": ""}', 'R test', True, True,
                'active',
                False
        ),

        (
                'rtest1@test.pl',
                'password',
                'password',
                '{"official_phone": "", '
                '"official_position": ""}',
                'R test',
                True,
                True,
                None,
                False
        ),
    ])
def test_user_form_validity(email, password1, password2, customfields, fullname, is_staff, is_superuser, state,
                            validity):
    form = UserCreationForm(data={
        'email': email,
        'password1': password1,
        'password2': password2,
        'customfields': customfields,
        'fullname': fullname,
        'is_staff': is_staff,
        'is_superuser': is_superuser,
        'state': state,
    })

    assert form.is_valid() is validity


@pytest.mark.django_db
def test_user_form_add_organization(valid_organization):
    form = UserCreationForm(data={
        'email': 'rtest1@wp.pl',
        'password1': '123',
        'password2': '123',
        'customfields': '{"official_phone": "", "official_position": ""}',
        'fullname': 'R K',
        'is_staff': True,
        'is_superuser': False,
        'state': 'pending',
        'organizations': [valid_organization]
    })
    assert form.is_valid() is True
    user = form.save()
    organization = Organization.objects.get(id=valid_organization.id)
    assert user in organization.users.all()

# @pytest.mark.django_db
# def test_user_form_customfields_field(valid_organization):
#     form = UserCreationForm(data={
#         'email': 'rtest1@wp.pl',
#         'password1': '123',
#         'password2': '123',
#         'customfields': {"official_phone": "123123123", "official_position": "test"},
#         'fullname': 'R K',
#         'is_staff': True,
#         'is_superuser': False,
#         'state': 'pending',
#         'organizations': [valid_organization]
#     })
#     assert form.is_valid() is True
#     user = form.save()
#     organization = Organization.objects.get(id=valid_organization.id)
#     assert user in organization.users.all()
#     assert user.customfields == {"official_phone": "123123123", "official_position": "test"}
