# import marshmallow
# import pytest
# from django.contrib.auth import get_user_model
#
# from mcod.users.schemas import AccountSchema, LoginSchema, RegistrationRequest
#
# User = get_user_model()
#
#
# @pytest.fixture()
# def db_user():
#     usr = User(
#         email='test@example.com',
#         password='S3cr3tPass',
#         state='active'
#     )
#     usr.save()
#     return usr
#
#
# @pytest.fixture()
# def user_dict():
#     return {
#         'id': 77,
#         'email': 'test@example.com',
#         'state': 'active'
#     }
#
#
# class Common(object):
#     def _test_serialized_user(self, user, schema):
#         d = schema().dump(user).data
#         result = schema().validate(d)
#         assert result == {}
#
#     def _test_email(self, user_dict, schema):
#         for wrong_email in ['abc', 'abc@', '@abc', 'abc@abc', '']:
#             user_dict['email'] = wrong_email
#             with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#                 schema().validate(user_dict)
#             assert 'email' in e.value.messages
#
#         user_dict.pop('email')
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             schema().validate(user_dict)
#         assert 'email' in e.value.messages
#
#
# class TestAccountSchema(Common):
#     @pytest.mark.django_db
#     def test_serialization_from_model(self, db_user):
#         self._test_serialized_user(db_user, AccountSchema)
#
#     def test_wrong_or_missing_email(self, user_dict):
#         self._test_email(user_dict, AccountSchema)
#
#     def test_wrong_or_missing_state(self, user_dict):
#         for wrong_state in ['abc', '', 1]:
#             user_dict['state'] = wrong_state
#             with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#                 AccountSchema().validate(user_dict)
#             assert 'state' in e.value.messages
#
#         user_dict.pop('state')
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             AccountSchema().validate(user_dict)
#         assert 'state' in e.value.messages
#
#
# class TestLoginSchema(Common):
#     @pytest.mark.django_db
#     def test_serialization_from_model(self, db_user):
#         db_user.token = 'abcdef'
#         self._test_serialized_user(db_user, LoginSchema)
#
#     def test_missing_token(self, user_dict):
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             LoginSchema().validate(user_dict)
#         assert 'token' in e.value.messages
#
#
# class TestRegistrationRequest():
#     def test_invalid_password(self, invalid_passwords):
#         for password in invalid_passwords:
#             data = {
#                 'email': 'test@mc.gov.pl',
#                 'password1': password,
#                 'password2': password
#             }
#
#             with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#                 RegistrationRequest().validate(data)
#             assert 'password1' in e.value.messages
#
#     def test_password_not_match(self):
#         data = {
#             'email': 'admin@mc.gov.pl',
#             'password1': 'e3!dEpc@7!',
#             'password2': 'e3!dEpc@7'
#         }
#
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             RegistrationRequest().validate(data)
#         assert 'password1' in e.value.messages
#         assert 'password2' in e.value.messages
#
#     def test_field_missing(self):
#         data = {
#             'email': 'admin@mc.gov.pl',
#             'password1': 'e3!dEpc@7!',
#         }
#
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             RegistrationRequest().validate(data)
#         assert 'password2' in e.value.messages
#
#         data = {
#             'email': 'admin@mc.gov.pl',
#             'password2': 'e3!dEpc@7!',
#         }
#
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             RegistrationRequest().validate(data)
#         assert 'password1' in e.value.messages
#
#         data = {
#             'password1': 'e3!dEpc@7!',
#             'password2': 'e3!dEpc@7!',
#         }
#
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             RegistrationRequest().validate(data)
#         assert 'email' in e.value.messages
#
#     def test_invalid_email(self):
#         data = {
#             'email': 'notanemailaddress@',
#             'password1': 'e3!dEpc@7!',
#             'password2': 'e3!dEpc@7!'
#         }
#         with pytest.raises(marshmallow.exceptions.ValidationError) as e:
#             RegistrationRequest().validate(data)
#         assert 'email' in e.value.messages
#
#     def test_valid_data(self):
#         data = {
#             'email': 'admin@mc.gov.pl',
#             'password1': 'e3!dEpc@7!',
#             'password2': 'e3!dEpc@7!'
#         }
#         result = RegistrationRequest().validate(data)
#         assert result == {}
