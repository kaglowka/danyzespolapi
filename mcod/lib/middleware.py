from django.db import connection
from mcod.lib.jwt import get_auth_token


class PostgresConfMiddleware(object):
    """ Simple middleware that adds the request object in thread local stor    age."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request, *args, **kwargs):
        # TODO - nie wpadam tutaj w czasie pracy z adminem
        if request.user.id:
            connection.cursor().execute(
                'SET myapp.userid = "{}"'.format(request.user.id)
            )

    def process_view(self, request, *args, **kwargs):
        if request.user.id:
            connection.cursor().execute(
                'SET myapp.userid = "{}"'.format(request.user.id)
            )


class UserTokenMiddleware(object):
    """
    Middleware to set user mcod_token cookie
    If user is authenticated and there is no cookie, set the cookie,
    If the user is not authenticated and the cookie remains, delete it
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_template_response(self, request, response):
        # if user and no cookie, set cookie
        domain = request.META.get("HTTP_HOST", "localhost")
        if domain.startswith('admin.'):
            domain = domain.replace('admin.', "")
        elif domain.startswith('localhost'):
            domain = domain.split(":")[0]

        if request.user.is_authenticated and not request.COOKIES.get('mcod_token'):
            token = get_auth_token(request.user.email, request.user.system_role, request.session.session_key)
            response.set_cookie("mcod_token", token, domain=domain)
        elif not request.user.is_authenticated:
            # else if no user and cookie remove user cookie, logout
            response.delete_cookie("mcod_token", domain=domain)

        return response
