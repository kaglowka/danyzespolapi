#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import django
import falcon.responders
import six
from falcon import COMBINED_METHODS
from falcon import routing
from webargs import falconparser

from mcod import settings
from mcod.counters.lib import CounterMiddleware
from mcod.lib.docs.resources import SwaggerResource, RestApispecResource, RPCApispecResource
from mcod.lib.errors import error_serializer, error_handler, error_422_handler, error_500_handler
from mcod.lib.middlewares.locale import LocaleMiddleware
from mcod.lib.middlewares.searchhistories import SearchHistoryMiddleware


class ApiApp(falcon.API):
    def add_routes(self, routes):
        for route in routes:
            self.add_route(*route)

    def add_route(self, uri_template, resource, custom_map=None, **kwargs):
        if not isinstance(uri_template, six.string_types):
            raise TypeError('uri_template is not a string')

        if not uri_template.startswith('/'):
            raise ValueError("uri_template must start with '/'")

        if '//' in uri_template:
            raise ValueError("uri_template may not contain '//'")

        method_map = self.map_http_methods(resource, custom_map)
        routing.set_default_responders(method_map)
        self._router.add_route(uri_template, method_map, resource, **kwargs)

    def map_http_methods(self, resource, custom_map=None):
        if not custom_map:
            return routing.map_http_methods(resource)

        method_map = {}
        for method in COMBINED_METHODS:
            if method in custom_map:
                responder = getattr(resource, custom_map[method])
                if callable(responder):
                    method_map[method] = responder
        return method_map


def get_api_app():
    from mcod.routes import routes

    app = ApiApp(middleware=[
        LocaleMiddleware(),
        CounterMiddleware(),
        SearchHistoryMiddleware(),
    ])

    # Additional routes
    routes += [
        ('/docs', SwaggerResource()),
        ('/spec/rest.json', RestApispecResource(app)),
        ('/spec/rpc.json', RPCApispecResource(app)),
    ]

    app.add_error_handler(falcon.HTTPError, error_handler)
    app.add_error_handler(falcon.HTTPInternalServerError, error_500_handler)
    app.add_error_handler(falconparser.HTTPError, error_422_handler)
    app.add_error_handler(falcon.HTTPUnprocessableEntity, error_422_handler)
    app.set_error_serializer(error_serializer)
    app.add_routes(routes)
    app.add_static_route(settings.STATIC_URL, settings.STATIC_ROOT)
    app.add_static_route(settings.MEDIA_URL, settings.MEDIA_ROOT)

    return app


django.setup()
app = get_api_app()

if __name__ == '__main__':
    from werkzeug.serving import run_simple

    run_simple('0.0.0.0', 8000, app, use_reloader=True)
