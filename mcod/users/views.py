# -*- coding: utf-8 -*-
from smtplib import SMTPException

import falcon
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from mcod import settings
from mcod.lib.handlers import (
    RetrieveOneHandler,
    CreateHandler,
    UpdateHandler
)
from mcod.lib.jwt import get_auth_token
from mcod.lib.triggers import session_store, LoginRequired
from mcod.lib.views import (
    CreateView,
    RetrieveOneView,
    UpdateView,
)
from mcod.users.models import Token
from mcod.users.schemas import (
    Login,
    Registration,
    AccountUpdate,
    PasswordChange,
    PasswordReset,
    PasswordResetConfirm,
    ResendActivationEmail
)
from mcod.users.serializers import (
    LoginSerializer,
    RegistrationSerializer,
    UserSerializer
)

User = get_user_model()


class LoginView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = Login()
        response_serializer = LoginSerializer(many=False, )  # include_data=('datasets',))

        def _data(self, request, cleaned, *args, **kwargs):
            try:
                user = User.objects.get(email=cleaned['email'])
            except User.DoesNotExist:
                raise falcon.HTTPUnauthorized(
                    title='401 Unauthorized',
                    description=_('Invalid email or password'),
                    code='account_not_exist'
                )

            if user.state is not 'active':
                if user.state not in settings.USER_STATE_LIST or user.state == 'deleted':
                    raise falcon.HTTPUnauthorized(
                        title='401 Unauthorized',
                        description=_('Account is not available'),
                        code='account_unavailable'
                    )

                if user.state in ('draft', 'blocked'):
                    raise falcon.HTTPUnauthorized(
                        title='401 Unauthorized',
                        description=_('Account is blocked'),
                        code='account_unavailable'
                    )

                if user.state == 'pending':
                    raise falcon.HTTPForbidden(
                        title='403 Forbidden',
                        description=_('Email addres not confirmed'),
                        code='account_inactive'
                    )

            user = authenticate(request=request, **cleaned)

            if user is None:
                raise falcon.HTTPUnauthorized(
                    title='401 Unauthorized',
                    description=_('Invalid email or password'),
                    code='authorization_error'
                )

            if not hasattr(request, 'session'):
                request.session = session_store()

                request.META = {}
            login(request, user)
            request.session.save()
            user.token = get_auth_token(user.email, user.system_role, request.session.session_key)

            return user


class RegistrationView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = Registration()
        response_serializer = RegistrationSerializer(many=False, )

        def _clean(self, request, *args, **kwargs):
            cleaned = super()._clean(request, *args, **kwargs)
            if User.objects.filter(email=cleaned['email']):
                raise falcon.HTTPForbidden(
                    title='403 Forbidden',
                    description=_('This e-mail is already used'),
                    code='emial_already_used'
                )
            return cleaned

        def _data(self, request, cleaned, *args, **kwargs):
            usr = User.objects.create_user(**cleaned)

            token = usr.email_validation_token
            link = settings.EMAIL_VALIDATION_URL % token
            # TODO: this is specific for mcod-backend, we should implement more generic solution
            try:
                conn = get_connection(settings.EMAIL_BACKEND)

                msg_plain = render_to_string('mails/confirm-registration.txt',
                                             {'link': link, 'host': settings.BASE_URL})
                msg_html = render_to_string('mails/confirm-registration.html',
                                            {'link': link, 'host': settings.BASE_URL})

                send_mail(
                    'Aktywacja konta',
                    msg_plain,
                    settings.NO_REPLY_EMAIL,
                    [usr.email, ],
                    connection=conn,
                    html_message=msg_html,
                )
            except SMTPException:
                raise falcon.HTTPInternalServerError(
                    description=_('Email cannot be send'),
                    code='email_send_error'
                )

            return usr


class AccountView(RetrieveOneView, UpdateView):
    class GET(RetrieveOneHandler):
        database_model = get_user_model()
        response_serializer = RegistrationSerializer(many=False, )
        triggers = [LoginRequired(), ]

        def _clean(self, request, *args, **kwargs):
            return request.user

    class PUT(UpdateHandler):
        database_model = get_user_model()
        request_schema = AccountUpdate()
        response_serializer = UserSerializer(many=False, )
        triggers = [LoginRequired(), ]


class LogoutView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        triggers = [LoginRequired(), ]

        def _clean(self, request, *args, **kwargs):
            return request.user

        def _data(self, request, cleaned, *args, **kwargs):
            logout(request)

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}


class ResetPasswordView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = PasswordReset()

        def _data(self, request, cleaned, *args, **kwargs):
            try:
                usr = User.objects.get(email=cleaned['email'])
            except User.DoesNotExist:
                raise falcon.HTTPNotFound(
                    description=_('Account not found'),
                    code='account_not_found'
                )

            reset_token = usr.password_reset_token
            link = settings.PASSWORD_RESET_URL % reset_token
            # TODO: this is specific for mcod-backend, we should implement more generic solution
            try:
                conn = get_connection(settings.EMAIL_BACKEND)

                msg_plain = render_to_string('mails/password-reset.txt', {'link': link, 'host': settings.BASE_URL})
                msg_html = render_to_string('mails/password-reset.html', {'link': link, 'host': settings.BASE_URL})

                send_mail(
                    'Reset hasła',
                    msg_plain,
                    settings.NO_REPLY_EMAIL,
                    [usr.email, ],
                    connection=conn,
                    html_message=msg_html
                )
            except SMTPException:
                raise falcon.HTTPInternalServerError(
                    description=_('Email cannot be send'),
                    code='email_send_error'
                )

            return usr

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {'result': 'ok'}


class ConfirmResetPasswordView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = PasswordResetConfirm()

        def _data(self, request, cleaned, token, *args, **kwargs):
            try:
                token = Token.objects.get(token=token, token_type=1)
            except Token.DoesNotExist:
                raise falcon.HTTPNotFound()

            if not token.is_valid:
                raise falcon.HTTPBadRequest(
                    description=_('Expired token'),
                    code='expired_token'
                )

            token.user.set_password(cleaned['new_password1'])
            token.user.save()
            token.invalidate()
            return token.user

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}


class ChangePasswordView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = PasswordChange()
        response_serializer = UserSerializer(many=False, )
        triggers = [LoginRequired(), ]

        def _data(self, request, cleaned, *args, **kwargs):
            request.user.set_password(cleaned['new_password1'])
            request.user.save()

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}


class VerifyEmailView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = get_user_model()

        def _clean(self, request, token, *args, **kwargs):
            try:
                token = Token.objects.get(token=token, token_type=0)
            except Token.DoesNotExist:
                raise falcon.HTTPNotFound()

            if not token.is_valid:
                raise falcon.HTTPBadRequest(
                    description=_('Expired token'),
                    code='expired_token'
                )

            if not token.user.email_confirmed:
                token.user.state = 'active' if token.user.state == 'pending' else token.user.state
                token.user.email_confirmed = timezone.now()
                token.user.save()
                token.invalidate()

        def _data(self, request, cleaned, *args, **kwargs):
            return {}

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}


class ResendActivationEmailView(CreateView):
    class POST(CreateHandler):
        database_model = get_user_model()
        request_schema = ResendActivationEmail()

        def _clean(self, request, *args, **kwargs):
            cleaned = super()._clean(request, *args, **kwargs)
            try:
                usr = User.objects.get(email=cleaned['email'])
            except User.DoesNotExist:
                raise falcon.HTTPNotFound(
                    description=_('Account not found'),
                    code='account_not_found'
                )
            return usr

        def _data(self, request, usr, *args, **kwargs):
            activation_token = usr.email_validation_token

            link = settings.EMAIL_VALIDATION_URL % activation_token
            try:
                conn = get_connection(settings.EMAIL_BACKEND)
                send_mail(
                    'Reset password',
                    link,
                    settings.NO_REPLY_EMAIL,
                    [usr.email, ], connection=conn
                )
            except SMTPException:
                raise falcon.HTTPInternalServerError(
                    description=_('Email cannot be send'),
                    code='email_send_error'
                )

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}
