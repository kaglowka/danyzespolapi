import pytest
from falcon import HTTP_OK, HTTP_NOT_FOUND, testing
from mcod.api import get_api_app
from mcod.lib.tests.helpers.elasticsearch import ElasticCleanHelper


@pytest.fixture()
def client():
    return testing.TestClient(get_api_app())


@pytest.mark.django_db
class TestArticlesView(ElasticCleanHelper):

    def test_noargs_get(self, client, articles_list):
        resp = client.simulate_get("/articles")
        assert HTTP_OK == resp.status
        body = resp.json
        for key in ('data', 'links', 'meta'):
            assert key in body
        assert type(body['data']) is list
        assert len(body['data']) == 3

        listed_articles = {article['id']: article for article in body['data']}
        for article in articles_list:
            if article.slug in ['article-deleted', 'article-draft']:
                assert article.id not in listed_articles
                continue
            assert article.id in listed_articles
            assert listed_articles[article.id]['attributes']['title'] == article.title
            assert listed_articles[article.id]['attributes']['slug'] == article.slug
            assert listed_articles[article.id]['links']['self'] == f'/articles/{article.id}'
            related_link = f'/articles/{article.id}/datasets'
            assert listed_articles[article.id]['relationships']['datasets']['links']['related']['href'] == related_link

            assert listed_articles[article.id]['type'] == 'articles'

    def test_query_get(self, client, articles_list):
        resp = client.simulate_get('/articles', params={'q': 'article'})
        assert HTTP_OK == resp.status
        body = resp.json
        for key in ('data', 'links', 'meta'):
            assert key in body
        assert type(body['data']) is list
        assert len(body['data']) == 2
        slugs = {article['attributes']['slug'] for article in body['data']}
        assert 'article-2' in slugs
        assert 'article-last' in slugs


@pytest.mark.django_db
class TestArticleView():
    def test_get_published(self, client, valid_article):
        resp = client.simulate_get(f'/articles/{valid_article.id}')
        assert HTTP_OK == resp.status

        for key in ('data', 'links', 'meta'):
            assert key in resp.json

        data = resp.json['data']
        meta = resp.json['meta']
        links = resp.json['links']
        assert data['type'] == 'articles'
        assert data['id'] == valid_article.id

        attrs = valid_article.__dict__
        for key in ('_state', 'id', 'status', 'status_changed', 'is_removed',
                    'created_by_id', 'modified_by_id', '_monitor_status_changed',
                    'uuid'):
            del attrs[key]
        attrs['created'] = attrs['created'].isoformat().replace('T', ' ')
        attrs['modified'] = attrs['modified'].isoformat().replace('T', ' ')
        attrs['tags'] = []
        attrs['followed'] = False
        attrs['license'] = None

        for key in data['attributes']:
            assert data['attributes'][key] == attrs[key]

        assert data['links']['self'] == links['self']
        assert data['links']['self'] == meta['path']

    def test_get_draft(self, client, draft_article):
        resp = client.simulate_get(f'/articles/{draft_article.id}')
        assert HTTP_NOT_FOUND == resp.status

    def test_get_draft_superuser(self, client, draft_article, admin_user):
        resp = client.simulate_post(path='/auth/login', json={
            'email': admin_user.email,
            'password': 'P4n.Samochodzik:)'
        })

        assert HTTP_OK == resp.status
        token = resp.json['data']['attributes']['token']

        resp = client.simulate_get(f'/articles/{draft_article.id}',
                                   headers={
                                       "Authorization": "Bearer %s" % token
                                   },

                                   )
        assert HTTP_OK == resp.status
