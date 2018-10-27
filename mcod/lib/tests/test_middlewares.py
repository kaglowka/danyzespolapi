from django.test import Client
import pytest


#
#
# @pytest.mark.run(order=0)
# def test_locale_middleware(client):
#     test_values = [
#         ('', 'pl', 'API działa!'),
#         ('*', 'pl', 'API działa!'),
#         ('zz', 'pl', 'API działa!'),
#         ('pl', 'pl', 'API działa!'),
#         ('pl-PL', 'pl', 'API działa!'),
#         ('pl,en', 'pl', 'API działa!'),
#         ('en', 'en', 'API works!'),
#         ('en-US', 'en', 'API works!'),
#         ('en,pl', 'en', 'API works!'),
#         ('en;q=1,pl;q=0.7,de;q=0.8', 'en', 'API works!'),
#         ('en;q=0.8,pl;q=0.9,de;q=0.7', 'pl', 'API działa!'),
#         ('en-US;q=0.9,pl-PL;q=1,de;q=0.7', 'pl', 'API działa!'),
#         ('en-US;q=0.9,pl-PL;q=0.6,de;q=0.7', 'en', 'API works!'),
#     ]
#     for header, lang, expected in test_values:
#         result = client.simulate_get('/', headers={
#             'Accept-Language': header
#         })
#
#         assert result.status == falcon.HTTP_200
#         # TODO: fix this
#         # assert result.json['result']['response'] == expected
#         assert result.headers['content-language'] == lang


@pytest.mark.django_db
def test_user_token_middleware(admin_user):
    client = Client()

    resp = client.get("/")
    assert resp.status_code == 302
    assert 'mcod_token' not in resp.cookies

    client.force_login(admin_user)
    resp = client.get("/")
    assert resp.status_code == 200
    assert 'mcod_token' in resp.cookies

    client.get('/logout/')
    resp = client.get('/')
    assert resp.status_code == 302
    assert 'mcod_token' not in resp.cookies
