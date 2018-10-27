# -*- coding: utf-8 -*-
import json

from django.utils.translation import gettext_lazy as _

from mcod.lib.encoders import LazyEncoder
from mcod.lib.schemas import ErrorSchema


def error_serializer(req, resp, exc):
    resp.body = exc.to_json()
    resp.content_type = 'application/json'
    resp.append_header('Vary', 'Accept')


def error_handler(exc, req, resp, params):
    resp.status = exc.status
    exc_data = {
        'title': exc.title,
        'description': exc.description,
        'code': getattr(exc, 'code') or 'error'
    }
    result, n = ErrorSchema().dump(exc_data)
    resp.body = json.dumps(result, cls=LazyEncoder)


def error_500_handler(exc, req, resp, params):
    resp.status = exc.status
    exc_data = {
        'title': exc.title,
        'description': _("Server error"),
        'code': getattr(exc, 'code') or 'server_error'
    }
    result, n = ErrorSchema().dump(exc_data)
    resp.body = json.dumps(result, cls=LazyEncoder)


def error_422_handler(exc, req, resp, params):
    resp.status = exc.status
    exc_data = {
        'title': exc.title,
        'description': _('Field value error'),
        'code': getattr(exc, 'code') or 'entity_error'
    }
    if hasattr(exc, 'errors'):
        exc_data['errors'] = exc.errors

    result, n = ErrorSchema().dump(exc_data)
    resp.body = json.dumps(result, cls=LazyEncoder)
