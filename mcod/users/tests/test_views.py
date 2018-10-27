# import pytest
# import smtplib
# from collections import namedtuple
#
# import falcon
# import os
# import shutil
# from django.contrib.auth import get_user_model
# from django.utils import timezone
#
# from mcod import settings
# from mcod.lib.caches import flush_sessions
# from mcod.lib.jwt import get_auth_header, decode_jwt_token
# from mcod.users.schemas import LoginResponse, AccountResponse
#
# User = get_user_model()
#
#
# @pytest.fixture()
# def fake_user():
#     return namedtuple('User', 'email state fullname')
#
#
# @pytest.fixture()
# def fake_session():
#     return namedtuple('Session', 'session_key')
#
#
# class TestLogin(object):
#     @pytest.mark.django_db
#     def test_active_user_login(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         assert LoginResponse().validate(resp.json) == {}
#
#     def test_wrong_body(self, client):
#         resp = client.simulate_post(path='/auth/login')
#         assert resp.status == falcon.HTTP_422
#
#         resp = client.simulate_post(path='/auth/login', json={
#             'password': 'secret_password'
#         })
#         assert resp.status == falcon.HTTP_422
#
#         resp = client.simulate_post(path='/auth/login', json={
#             'aaaaa': 'bbbbb'
#         })
#
#         assert resp.status == falcon.HTTP_422
#
#     @pytest.mark.django_db
#     def test_wrong_email(self, client):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': 'doesnotexist@example.com',
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'account_not_exist'
#
#         for email in ['aaa', 'aaa@', '@aaa', 'aaa@aaa']:
#             resp = client.simulate_post(path='/auth/login', json={
#                 'email': email,
#                 'password': 'P4n.Samochodzik:)'
#             })
#
#             assert resp.status == falcon.HTTP_422
#             assert resp.json['code'] == 'entity_error'
#
#     @pytest.mark.django_db
#     def test_wrong_password(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)5'
#         })
#
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'authorization_error'
#
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'abcd'
#         })
#
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'authorization_error'
#
#     @pytest.mark.django_db
#     def test_pending_user(self, client, inactive_user):
#         req_data = {
#             'email': inactive_user.email,
#             'password': 'P4n.Samochodzik:)'
#         }
#         resp = client.simulate_post(path='/auth/login', json=req_data)
#         assert resp.status == falcon.HTTP_403
#         assert resp.json['code'] == 'account_inactive'
#
#     @pytest.mark.django_db
#     def test_deleted_user(self, client, deleted_user):
#         req_data = {
#             'email': deleted_user.email,
#             'password': 'P4n.Samochodzik:)'
#         }
#         resp = client.simulate_post(path='/auth/login', json=req_data)
#         assert resp.status == falcon.HTTP_403
#         assert resp.json['code'] == 'account_inactive'
#
#     @pytest.mark.django_db
#     def test_blocked_user(self, client, blocked_user):
#         req_data = {
#             'email': blocked_user.email,
#             'password': 'P4n.Samochodzik:)'
#         }
#         resp = client.simulate_post(path='/auth/login', json=req_data)
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'account_unavailable'
#
#     def test_unknown_state_user(self, client, fake_user, fake_session, mocker):
#         usr = fake_user(
#             email='test@example.com', state='unknown_state', fullname='Test Example'
#         )
#         mocker.patch('mcod.users.resources.login')
#         mocker.patch('mcod.users.resources.session_store', return_value=fake_session(
#             session_key=1234
#         ))
#
#         mocker.patch('mcod.users.resources.User.objects.get', return_value=usr)
#
#         mocker.patch('mcod.users.resources.authenticate', return_value=usr)
#
#         req_data = {
#             'email': 'test@example.com',
#             'password': 'secret_password'
#         }
#
#         resp = client.simulate_post(path='/auth/login', json=req_data)
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'account_unavailable'
#
#
# class TestRegistration(object):
#     @pytest.mark.django_db
#     def test_required_fields(self, client):
#         req_data = {
#             'fullname': 'Test User'
#         }
#         resp = client.simulate_post(path='/auth/registration', json=req_data)
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'email' in resp.json['errors']
#         assert 'password1' in resp.json['errors']
#         assert 'password2' in resp.json['errors']
#
#     def test_invalid_email(self, client):
#         req_data = {
#             'email': 'not_valid@email',
#             'password1': '123!a!b!c!',
#             'password2': '123!a!b!c!',
#         }
#         resp = client.simulate_post(path='/auth/registration', json=req_data)
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'email' in resp.json['errors']
#
#     @pytest.mark.django_db
#     def test_invalid_password(self, client):
#         req_data = {
#             'email': 'test@mc.gov.pl',
#             'password1': '123.aBc',
#             'password2': '123.aBc',
#         }
#         resp = client.simulate_post(path='/auth/registration', json=req_data)
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'password1' in resp.json['errors']
#         assert 'password2' not in resp.json['errors']
#
#         req_data = {
#             'email': 'test@mc.gov.pl',
#             'password1': '12.34a.bCd!',
#             'password2': '12.34a.bCd!!',
#         }
#         resp = client.simulate_post(path='/auth/registration', json=req_data)
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'password1' in resp.json['errors']
#         assert 'password2' in resp.json['errors']
#
#     # TODO: fix this
#     # @pytest.mark.django_db
#     # def test_valid_registration(self, client):
#     #     req_data = {
#     #         'email': 'tester@mc.gov.pl',
#     #         'password1': '123!A!b!c!',
#     #         'password2': '123!A!b!c!',
#     #     }
#     #     resp = client.simulate_post(path='/auth/registration', json=req_data)
#     #     assert resp.status == falcon.HTTP_200
#     #     assert 'result' in resp.json
#     #     result = resp.json['result']
#     #     assert set(('email', 'id', 'state')) <= set(result)
#     #     assert not set(('password1', 'password2', 'fullname', 'customfields')) <= set(result)
#     #     assert result['state'] == 'pending'
#     #     assert AccountResponse().validate(resp.json) == {}
#     #
#     #     req_data['email'] = 'tester2@mc.gov.pl'
#     #     req_data['fullname'] = 'Test User 2'
#     #     req_data['customfields'] = {'value':"Lorem ipsum..."}
#     #
#     #     shutil.rmtree(settings.EMAIL_FILE_PATH, ignore_errors=True)
#     #
#     #     resp = client.simulate_post(path='/auth/registration', json=req_data)
#     #     assert resp.status == falcon.HTTP_200
#     #     assert 'result' in resp.json
#     #     result = resp.json['result']
#     #     assert set(('email', 'id', 'state', 'fullname', 'customfields')) <= set(result)
#     #     assert not set(('password1', 'password2')) <= set(result)
#     #     assert result['state'] == 'pending'
#     #     assert result['fullname'] == req_data['fullname']
#     #     assert result['customfields'] == req_data['customfields']
#     #     assert AccountResponse().validate(resp.json) == {}
#     #
#     #     assert len(os.listdir(settings.EMAIL_FILE_PATH)) == 1
#     #     filename = os.path.join(settings.EMAIL_FILE_PATH, os.listdir(settings.EMAIL_FILE_PATH)[0])
#     #     f = open(filename)
#     #     assert 'To: %s' % req_data['email'] in f.read()
#     #     f.seek(0)
#     #
#     #     usr = User.objects.get(email=req_data['email'])
#     #     token = usr.email_validation_token
#     #     link = settings.EMAIL_VALIDATION_URL % token
#     #     assert link in f.read()
#
#     # TODO: fix this
#     # @pytest.mark.django_db
#     # def test_registration_account_already_exist(self, client):
#     #     req_data = {
#     #         'email': 'tester@mc.gov.pl',
#     #         'password1': '123!a!B!c!',
#     #         'password2': '123!a!B!c!',
#     #     }
#     #     resp = client.simulate_post(path='/auth/registration', json=req_data)
#     #     assert resp.status == falcon.HTTP_200
#     #     resp = client.simulate_post(path='/auth/registration', json=req_data)
#     #     assert resp.status == falcon.HTTP_403
#
#     # TODO: fix this
#     # @pytest.mark.django_db
#     # def test_registration_can_change_user_state(self, client):
#     #     req_data = {
#     #         'email': 'tester@mc.gov.pl',
#     #         'password1': '123!a!B!c!',
#     #         'password2': '123!a!B!c!',
#     #         'state': 'active'
#     #     }
#     #     resp = client.simulate_post(path='/auth/registration', json=req_data)
#     #     assert resp.status == falcon.HTTP_200
#     #     assert 'result' in resp.json
#     #     result = resp.json['result']
#     #     assert result['state'] == 'pending'
#     #     usr = User.objects.get(id=result['id'])
#     #     assert usr.state == 'pending'
#
#
# class TestLogout(object):
#
#     def test_logout_by_not_logged_in(self, client):
#         resp = client.simulate_post(path='/auth/logout')
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'token_missing'
#
#     @pytest.mark.django_db
#     def test_logout(self, client, active_user):
#         flush_sessions()
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         active_usr_token = resp.json['result']['token']
#         session_valid = active_user.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr_token))
#
#         assert resp.status == falcon.HTTP_200
#         assert session_valid is True
#
#         active_user2 = User.objects.create_user('test-active2@example.com', 'P4n.Samochodzik:)')
#         active_user2.state = 'active'
#         active_user2.save()
#
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user2.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#
#         active_usr2_token = resp.json['result']['token']
#         session_valid = active_user.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr_token))
#         assert session_valid is True
#         session_valid = active_user2.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr2_token))
#         assert session_valid is True
#
#         resp = client.simulate_post(path='/auth/logout', headers={
#             "Authorization": "Bearer %s" % active_usr_token
#         })
#
#         assert resp.status == falcon.HTTP_200
#         session_valid = active_user.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr_token))
#         assert session_valid is False
#         session_valid = active_user2.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr2_token))
#         assert session_valid is True
#
#         resp = client.simulate_post(path='/auth/logout', headers={
#             "Authorization": "Bearer %s" % active_usr2_token
#         })
#
#         assert resp.status == falcon.HTTP_200
#         session_valid = active_user.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr_token))
#         assert session_valid is False
#         session_valid = active_user2.check_session_valid('%s %s' % (settings.JWT_HEADER_PREFIX, active_usr2_token))
#         assert session_valid is False
#
#
# class TestProfile(object):
#     def test_get_profile_not_logged_user(self, client):
#         resp = client.simulate_get(path='/auth/user')
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'token_missing'
#
#     @pytest.mark.django_db
#     def test_get_profile_after_logout(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         token = resp.json['result']['token']
#
#         resp = client.simulate_post(path='/auth/logout', headers={
#             "Authorization": "Bearer %s" % token
#         })
#
#         assert resp.status == falcon.HTTP_200
#
#         resp = client.simulate_get(path='/auth/user', headers={
#             "Authorization": "Bearer %s" % token
#         })
#         assert resp.status == falcon.HTTP_401
#         assert resp.json['code'] == 'authentication_error'
#
#     @pytest.mark.django_db
#     def test_get_valid_profile(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         token = resp.json['result']['token']
#         resp = client.simulate_get(path='/auth/user', headers={
#             "Authorization": "Bearer %s" % token
#         })
#         assert resp.status == falcon.HTTP_200
#         assert 'result' in resp.json
#         result = resp.json['result']
#         assert set(('email', 'id', 'state')) <= set(result)
#         assert not set(('password1', 'password2', 'fullname', 'customfields')) <= set(result)
#         assert result['state'] == 'active'
#         assert AccountResponse().validate(resp.json) == {}
#
#     @pytest.mark.django_db
#     def test_profile_update(self, client, active_user, inactive_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         token = resp.json['result']['token']
#         resp = client.simulate_put(path='/auth/user', headers={
#             "Authorization": "Bearer %s" % token}, json={
#             "fullname": "AAAA BBBB",
#             "customfields": {'value': "Lorem ipsum"},
#             "state": "blocked",
#             "email": "inny@email.com"
#         })
#         assert resp.status == falcon.HTTP_200
#         assert resp.json['result']['fullname'] == 'AAAA BBBB'
#         # TODO: fix this
#         # assert resp.json['result']['customfields']['value'] == 'Lorem ipsum'
#         assert resp.json['result']['state'] == active_user.state
#         assert resp.json['result']['email'] == active_user.email
#
#
# class TestResetPassword(object):
#     @pytest.mark.django_db
#     def test_sending_email(self, client, active_user):
#         shutil.rmtree(settings.EMAIL_FILE_PATH, ignore_errors=True)
#
#         resp = client.simulate_post(path='/auth/password/reset', json={
#             'email': active_user.email,
#         })
#
#         assert resp.status == falcon.HTTP_200
#         assert len(os.listdir(settings.EMAIL_FILE_PATH)) == 1
#         filename = os.path.join(settings.EMAIL_FILE_PATH, os.listdir(settings.EMAIL_FILE_PATH)[0])
#         f = open(filename)
#         assert 'To: %s' % active_user.email in f.read()
#         f.seek(0)
#         link = settings.PASSWORD_RESET_URL % active_user.password_reset_token
#         assert link in f.read()
#
#     @pytest.mark.django_db
#     def test_wrong_email(self, client, active_user):
#         resp = client.simulate_post(path='/auth/password/reset', json={
#             'email': 'wrong_email_address',
#         })
#
#         assert resp.status == falcon.HTTP_422
#
#         resp = client.simulate_post(path='/auth/password/reset', json={
#             'email': 'this_email@doesnotex.ist',
#         })
#
#         assert resp.status == falcon.HTTP_404
#
#     @pytest.mark.django_db
#     def test_smtp_backend_error(self, client, active_user, mocker):
#         mocker.patch('mcod.users.resources.send_mail', side_effect=smtplib.SMTPException)
#         resp = client.simulate_post(path='/auth/password/reset', json={
#             'email': active_user.email,
#         })
#
#         assert resp.status == falcon.HTTP_500
#
#
# class TestResetPasswordConfirm(object):
#     @pytest.mark.django_db
#     def test_password_change(self, client, active_user):
#         data = {
#             'new_password1': '123.4.bce',
#             'new_password2': '123.4.bce'
#         }
#         token = active_user.password_reset_token
#         url = '/auth/password/reset/%s' % token
#
#         resp = client.simulate_post(url, json=data)
#         assert resp.status == falcon.HTTP_422
#         assert 'new_password1' in resp.json['errors']
#
#         data = {
#             'new_password1': '123.4.bCe',
#             'new_password2': '123.4.bCe!'
#         }
#
#         resp = client.simulate_post(url, json=data)
#         assert resp.status == falcon.HTTP_422
#         assert 'new_password1' in resp.json['errors']
#
#         valid_data = {
#             'new_password1': '123.4.bCe',
#             'new_password2': '123.4.bCe'
#         }
#
#         resp = client.simulate_post(url, json=valid_data)
#         assert resp.status == falcon.HTTP_200
#         usr = User.objects.get(pk=active_user.id)
#         assert usr.check_password(valid_data['new_password1']) is True
#         t = usr.tokens.filter(token=token).first()
#         assert t is not None
#         assert t.is_valid is False
#
#     @pytest.mark.django_db
#     def test_invalid_expired_token(self, client, active_user):
#         url = '/auth/password/reset/abcdedfg'
#
#         data = {
#             'new_password1': '123.4.bcE',
#             'new_password2': '123.4.bcE'
#         }
#
#         resp = client.simulate_post(url, json=data)
#         assert resp.status == falcon.HTTP_404
#
#         url = '/auth/password/reset/8c37fd0c-5600-4277-a13a-67ced4a61e66'
#
#         data = {
#             'new_password1': '123.4.bcE',
#             'new_password2': '123.4.bcE'
#         }
#
#         resp = client.simulate_post(url, json=data)
#         assert resp.status == falcon.HTTP_404
#
#         token = active_user.password_reset_token
#
#         token_obj = active_user.tokens.filter(token=token).first()
#
#         assert token_obj.is_valid is True
#
#         token_obj.invalidate()
#
#         assert token_obj.is_valid is False
#
#         url = '/auth/password/reset/%s' % token
#
#         resp = client.simulate_post(url, json=data)
#         assert resp.status == falcon.HTTP_400
#         assert resp.json['code'] == 'expired_token'
#
#
# class TestChangePassword(object):
#     @pytest.mark.django_db
#     def test_password_change_errors(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         token = resp.json['result']['token']
#
#         resp = client.simulate_post(path='/auth/password/change',
#                                     headers={
#                                         "Authorization": "Bearer %s" % token
#                                     },
#                                     json={
#                                         "old_password": "AAAA.BBBB12",
#                                         "new_password1": "AaCc.5922",
#                                         "new_password2": "AaCc.5922",
#                                     })
#
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'old_password' in resp.json['errors']
#
#         resp = client.simulate_post(path='/auth/password/change',
#                                     headers={
#                                         "Authorization": "Bearer %s" % token
#                                     },
#                                     json={
#                                         "old_password": "P4n.Samochodzik:)",
#                                         "new_password1": "AaCc.5922",
#                                         "new_password2": "AaCc.59222",
#                                     })
#
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'new_password1' in resp.json['errors']
#         assert 'new_password2' in resp.json['errors']
#
#         resp = client.simulate_post(path='/auth/password/change',
#                                     headers={
#                                         "Authorization": "Bearer %s" % token
#                                     },
#                                     json={
#                                         "old_password": "P4n.Samochodzik:)",
#                                         "new_password1": "Abcde",
#                                         "new_password2": "Abcde",
#                                     })
#
#         assert resp.status == falcon.HTTP_422
#         assert resp.json['code'] == 'entity_error'
#         assert 'new_password1' in resp.json['errors']
#         assert 'new_password2' not in resp.json['errors']
#
#     @pytest.mark.django_db
#     def test_password_change(self, client, active_user):
#         resp = client.simulate_post(path='/auth/login', json={
#             'email': active_user.email,
#             'password': 'P4n.Samochodzik:)'
#         })
#
#         assert resp.status == falcon.HTTP_200
#         token = resp.json['result']['token']
#
#         data = {
#             "old_password": "P4n.Samochodzik:)",
#             "new_password1": "AaCc.5922",
#             "new_password2": "AaCc.5922",
#         }
#         resp = client.simulate_post(path='/auth/password/change',
#                                     headers={
#                                         "Authorization": "Bearer %s" % token
#                                     },
#                                     json=data)
#
#         assert resp.status == falcon.HTTP_200
#
#         usr = User.objects.get(pk=active_user.id)
#         assert usr.check_password(data['new_password1']) is True
#
#
# class TestResendActivationMail(object):
#     @pytest.mark.django_db
#     def test_resending(self, client, inactive_user):
#         shutil.rmtree(settings.EMAIL_FILE_PATH, ignore_errors=True)
#         resp = client.simulate_post(path='/auth/registration/resend-email',
#                                     json={
#                                         'email': inactive_user.email
#                                     }
#                                     )
#         assert resp.status == falcon.HTTP_200
#         assert 'result' in resp.json
#
#         assert len(os.listdir(settings.EMAIL_FILE_PATH)) == 1
#         filename = os.path.join(settings.EMAIL_FILE_PATH, os.listdir(settings.EMAIL_FILE_PATH)[0])
#         f = open(filename)
#         assert 'To: %s' % inactive_user.email in f.read()
#         f.seek(0)
#
#         usr = User.objects.get(email=inactive_user.email)
#         token = usr.email_validation_token
#         link = settings.EMAIL_VALIDATION_URL % token
#         assert link in f.read()
#
#     @pytest.mark.django_db
#     def test_wrong_email(self, client):
#         data = {
#             'email': 'this_is_so_wrong'
#         }
#
#         resp = client.simulate_post(path='/auth/registration/resend-email', json=data)
#         assert resp.status == falcon.HTTP_422
#         assert 'email' in resp.json['errors']
#
#         data = {
#             'email': 'not_existing_email@example.com'
#         }
#
#         resp = client.simulate_post(path='/auth/registration/resend-email', json=data)
#         assert resp.status == falcon.HTTP_404
#
#     @pytest.mark.django_db
#     def test_smtp_backend_error(self, active_user, client, mocker):
#         mocker.patch('mcod.users.resources.send_mail', side_effect=smtplib.SMTPException)
#         resp = client.simulate_post(path='/auth/registration/resend-email', json={
#             'email': active_user.email,
#         })
#
#         assert resp.status == falcon.HTTP_500
#
#
# class TestVerifyEmail(object):
#     @pytest.mark.django_db
#     def test_pending_user(self, client, inactive_user):
#         token = inactive_user.email_validation_token
#         resp = client.simulate_get(path='/user/verify-email/%s/' % token)
#         assert resp.status == falcon.HTTP_200
#
#         usr = User.objects.get(email=inactive_user)
#         assert usr.state == 'active'
#         token_obj = usr.tokens.filter(token=token).first()
#         assert token_obj.is_valid is False
#         assert usr.email_confirmed.date() == timezone.now().date()
#
#     @pytest.mark.django_db
#     def test_blocked_user(self, client, blocked_user):
#         token = blocked_user.email_validation_token
#         resp = client.simulate_get(path='/auth/registration/verify-email/%s/' % token)
#         assert resp.status == falcon.HTTP_200
#
#         usr = User.objects.get(email=blocked_user)
#         assert usr.state == 'blocked'
#         token_obj = usr.tokens.filter(token=token).first()
#         assert token_obj.is_valid is False
#         assert usr.email_confirmed.date() == timezone.now().date()
#
#     @pytest.mark.django_db
#     def test_errors(self, client, inactive_user):
#         resp = client.simulate_get(path='/auth/registration/verify-email/abcdef')
#         assert resp.status == falcon.HTTP_404
#
#         resp = client.simulate_get(path='/auth/registration/verify-email/8c37fd0c-5600-4277-a13a-67ced4a61e66')
#         assert resp.status == falcon.HTTP_404
#
#         v = inactive_user.email_validation_token
#         token = inactive_user.tokens.filter(token=v).first()
#         assert token.is_valid is True
#
#         token.invalidate()
#
#         resp = client.simulate_get(path='/auth/registration/verify-email/%s' % v)
#         assert resp.status == falcon.HTTP_400
#
#
# class TestAdminPanelAccess(object):
#     @pytest.mark.django_db
#     def test_extended_permissions(self, active_user):
#         header = get_auth_header(
#             active_user.email,
#             active_user.system_role,
#             '1'
#         )
#
#         payload = decode_jwt_token(header)
#         assert payload['user']['role'] == 'user'
#
#         active_user.is_staff = True
#
#         header = get_auth_header(
#             active_user.email,
#             active_user.system_role,
#             '1'
#         )
#
#         payload = decode_jwt_token(header)
#         assert payload['user']['role'] == 'staff'
#
#         active_user.is_staff = False
#         active_user.is_superuser = True
#
#         header = get_auth_header(
#             active_user.email,
#             active_user.system_role,
#             '1'
#         )
#
#         payload = decode_jwt_token(header)
#         assert payload['user']['role'] == 'staff'
