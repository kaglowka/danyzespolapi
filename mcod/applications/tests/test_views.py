import pytest
from falcon import HTTP_OK, HTTP_NOT_FOUND, HTTP_UNPROCESSABLE_ENTITY

from mcod.lib.tests.helpers.elasticsearch import ElasticCleanHelper


# @pytest.mark.django_db
# def test_application_history(client, valid_application):
#     resp = client.simulate_get(f"/applications/{valid_application.id}/history")
#     assert resp.status == HTTP_OK


@pytest.mark.django_db
class TestApplicationsView(ElasticCleanHelper):
    def test_noargs_get(self, client, applications_list):
        resp = client.simulate_get('/applications')
        assert HTTP_OK == resp.status
        body = resp.json
        for key in ('data', 'links', 'meta'):
            assert key in body
        assert type(body['data']) is list
        assert len(body['data']) == 3

        listed_apps = {app['id']: app for app in body['data']}
        for app in applications_list:
            if app.slug == 'app-del':
                assert app.id not in listed_apps
                continue
            assert app.id in listed_apps
            assert listed_apps[app.id]['attributes']['title'] == app.title
            assert listed_apps[app.id]['attributes']['slug'] == app.slug
            assert listed_apps[app.id]['attributes']['url'] == app.url

            assert listed_apps[app.id]['links']['self'] == f'/applications/{app.id}'
            assert listed_apps[app.id]['relationships']['datasets']['links']['related']['href'] == \
                f'/applications/{app.id}/datasets'
            assert listed_apps[app.id]['type'] == 'applications'

    def test_query_get(self, client, applications_list):
        resp = client.simulate_get('/applications', params={'q': 'application'})
        assert HTTP_OK == resp.status
        body = resp.json

        for key in ('data', 'links', 'meta'):
            assert key in body
        assert type(body['data']) is list
        assert len(body['data']) == 2
        titles = {app['attributes']['title'] for app in body['data']}
        assert 'Deleted application' not in titles
        assert 'Test name' not in titles


@pytest.mark.django_db
class TestApplicationView(object):
    def test_valid_get(self, client, valid_application):
        resp = client.simulate_get(f'/applications/{valid_application.id}')
        assert HTTP_OK == resp.status

        for key in ('data', 'links', 'meta'):
            assert key in resp.json

        data = resp.json['data']
        meta = resp.json['meta']
        links = resp.json['links']
        assert data['type'] == 'applications'
        assert data['id'] == valid_application.id

        attrs = valid_application.__dict__
        for key in ('_state', 'id', 'status', 'status_changed', 'is_removed', 'image',
                    'created_by_id', 'modified_by_id', '_monitor_status_changed',
                    'uuid'):
            del attrs[key]
        attrs['created'] = attrs['created'].isoformat().replace('T', ' ')
        attrs['modified'] = attrs['modified'].isoformat().replace('T', ' ')
        attrs['image_url'] = ''
        attrs['tags'] = []
        attrs['followed'] = False

        for key in data['attributes']:
            assert data['attributes'][key] == attrs[key]

        assert data['links']['self'] == links['self']
        assert data['links']['self'] == meta['path']

    def test_get_invalid_id(self, client, valid_application):
        resp = client.simulate_get('/applications/!nV')
        assert HTTP_NOT_FOUND == resp.status

        resp = client.simulate_get(f'/applications/{valid_application.id+10}')
        assert HTTP_NOT_FOUND == resp.status

    def test_get_deleted(self, client, valid_application):
        del_id = valid_application.id
        valid_application.delete()

        resp = client.simulate_get(f'/applications/{del_id}')
        assert HTTP_NOT_FOUND == resp.status


@pytest.mark.django_db
class TestApplicationDatasetsView(object):
    def test_valid_get(self, client, valid_application):
        resp = client.simulate_get(f'/applications/{valid_application.id}/datasets')
        assert resp.status == HTTP_OK

        assert len(resp.json['data']) == 0
        # TODO dorobić fixture dataset dla valid_application i sprawdzic jego pola

        assert all((key in resp.json['links']) for key in ('first', 'self'))
        assert resp.json['links']['first'] == f'/applications/{valid_application.id}/datasets?page=1&per_page=20'
        assert resp.json['links']['first'] == resp.json['links']['self']


@pytest.mark.django_db
class TestApplicationProposalForm(object):
    minimal_json = {
        "title": "tytuł",
        "notes": "ble\nbleble\nala ma kota",
        "applicant_email": "anuone@anywhere.any",
        "url": "http://www.google.pl",
    }

    def test_valid_full_post(self, client):
        json = self.minimal_json.copy()
        json["datasets"] = [1, 2, 3]
        json["image"] = "data:image/png;base64,SoMeBaSE64iMAge=="

        resp = client.simulate_post(
            path='/applications/propose',
            json=json
        )

        assert resp.status == HTTP_OK
        assert resp.json == {}

    def test_valid_min_post(self, client):
        resp = client.simulate_post(
            path='/applications/propose',
            json=self.minimal_json
        )

        assert resp.status == HTTP_OK
        assert resp.json == {}

    def test_missing_fields_posts(self, client):
        for key in self.minimal_json:
            json = self.minimal_json.copy()
            del json[key]

            resp = client.simulate_post(
                path='/applications/propose',
                json=json
            )
            assert resp.status == HTTP_UNPROCESSABLE_ENTITY

    def test_invalid_email(self, client):
        json = self.minimal_json.copy()
        json['applicant_email'] = "invalid@mail"

        resp = client.simulate_post(
            path='/applications/propose',
            json=json
        )
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

    def test_invalid_url(self, client):
        json = self.minimal_json.copy()
        json['url'] = "invalid[]url,^&*"

        resp = client.simulate_post(
            path='/applications/propose',
            json=json
        )
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY

    def test_invalid_datasets(self, client):
        json = self.minimal_json.copy()
        json['datasets'] = 'app is using all dataset'

        resp = client.simulate_post(
            path='/applications/propose',
            json=json
        )
        assert resp.status == HTTP_UNPROCESSABLE_ENTITY
