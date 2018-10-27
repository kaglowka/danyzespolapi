import pytest
import elasticsearch_dsl
from collections import namedtuple
from django.contrib.auth import get_user_model
from django.core.cache import caches
from falcon import testing

from mcod import settings
from mcod.api import app
from mcod.applications.models import Application
from mcod.articles.models import Article
from mcod.categories.models import Category
from mcod.datasets.models import Dataset
from mcod.organizations.models import Organization
from mcod.resources.models import Resource
from mcod.tags.models import Tag

User = get_user_model()


@pytest.fixture
def client():
    return testing.TestClient(app)


@pytest.fixture
def token_exp_delta():
    return 315360000  # 10 years


@pytest.fixture
def active_user():
    usr = User.objects.create_user('test-active@example.com', 'P4n.Samochodzik:)')
    usr.state = 'active'
    usr.save()
    return usr


@pytest.fixture
def admin_user():
    usr = User.objects.create_user('test-admin@example.com', 'P4n.Samochodzik:)')
    usr.state = 'active'
    usr.is_staff = True
    usr.is_superuser = True
    usr.save()
    return usr


@pytest.fixture
def admin_user2():
    usr = User.objects.create_user('test-admin2@example.com', 'P4n.Samochodzik:)')
    usr.state = 'active'
    usr.is_staff = True
    usr.is_superuser = True
    usr.save()
    return usr


@pytest.fixture
def editor_user():
    usr = User.objects.create_user('test-editor@example.com', 'P4n.Samochodzik:)')
    usr.state = 'active'
    usr.is_staff = True
    usr.save()
    return usr


@pytest.fixture
def inactive_user():
    usr = User.objects.create_user('test-inactive@example.com', 'P4n.Samochodzik:)')
    return usr


@pytest.fixture
def blocked_user():
    usr = User.objects.create_user('test-blocked@example.com', 'P4n.Samochodzik:)')
    usr.state = 'blocked'
    usr.save()
    return usr


@pytest.fixture
def user_with_organization(valid_organization):
    usr = User.objects.create_user('test-editor@example.com', 'P4n.Samochodzik:)')
    usr.state = 'active'
    usr.organizations.set([valid_organization])
    usr.is_staff = True
    usr.save()
    return usr


@pytest.fixture
def deleted_user():
    usr = User.objects.create_user('test-deleted@example.com', 'P4n.Samochodzik:)')
    usr.is_removed = True
    usr.save()
    return usr


# @pytest.fixture
# def draft_user():
#     usr = User.objects.create_user('test-draft@example.com', 'P4n.Samochodzik:)')
#     usr.state = 'draft'
#     usr.save()
#     return usr


@pytest.fixture
def sessions_cache():
    return caches[settings.SESSION_CACHE_ALIAS]


@pytest.fixture
def default_cache():
    return caches['default']


@pytest.fixture
def invalid_passwords():
    return [
        'abcd1234',
        'abcdefghi',
        '123456789',
        'alpha101',
        '92541001101',
        '9dragons',
        '@@@@@@@@',
        '.........',
        '!!!!!!!!!!!',
        '12@@@@@@@',
        '!!@#$$@ab@@',
        'admin@mc.gov.pl',
        '1vdsA532A66',
    ]


@pytest.fixture
def invalid_passwords_with_user():
    return [
        'abcd1234',
        'abcdefghi',
        '123456789',
        'aaa@bbb.cc',
        'aaa@bbb.c12',
        'bbb@aaa.cc',
        'TestUser123',
        'Test User',
        'Test.User',
        'User.Test123',
        'alpha101',
        '92541001101',
        '9dragons',
        '@@@@@@@@',
        '.........',
        '!!!!!!!!!!!',
        '12@@@@@@@',
        '!!@#$$@ab@@',
        'admin@mc.gov.pl',
        '1vdsA532A66',
    ]


@pytest.fixture
def valid_passwords():
    passwords = [
        '12@@@@@@Ab@',
        '!!@#$$@aBB1@@',
        'Iron.Man.Is.Th3.Best'
        'Admin7@mc.gov.pl',
        '1vDsA532A.6!6',
    ]
    passwords.extend(['Abcd%s1234' % v for v in settings.SPECIAL_CHARS])
    return passwords


@pytest.fixture
def valid_organization():
    organization = Organization()
    organization.slug = "test"
    organization.title = "test"
    organization.postal_code = "00-001"
    organization.city = "Warszwa"
    organization.street = "Królewska"
    organization.street_number = "27"
    organization.flat_number = "1"
    organization.street_type = "ul"
    organization.email = "email@email.pl"
    organization.fax = "123123123"
    organization.tel = "123123123"
    organization.epuap = "epuap"
    organization.regon = "123123123"
    organization.website = "www.www.www"
    organization.save()
    return organization


@pytest.fixture
def valid_organization2():
    organization = Organization()
    organization.slug = "zlodzieje-cienia"
    organization.title = "Złodzieje cienia"
    organization.postal_code = "00-002"
    organization.city = "Wrota Baldura"
    organization.street = "Schowana"
    organization.street_number = "3"
    organization.flat_number = "1"
    organization.street_type = "ul"
    organization.email = "email@shadowthieves.bg"
    organization.fax = "321321321"
    organization.tel = "321321321"
    organization.epuap = "shthv"
    organization.regon = "321321321"
    organization.website = "www.shadowthieves.bg"
    organization.save()
    return organization


@pytest.fixture
def inactive_organization():
    organization = Organization()
    organization.slug = "test"
    organization.title = "test"
    return organization


@pytest.fixture
def articles_list():
    a2 = Article()
    a2.slug = "article-2"
    a2.title = "Article 2"
    a2.status = "published"
    a2.save()

    del_a2 = Article()
    del_a2.slug = "article-deleted"
    del_a2.title = "Article Deleted"
    del_a2.status = "published"
    del_a2.save()
    del_a2.delete()

    a_draft = Article()
    a_draft.slug = "article-draft"
    a_draft.title = "Article draft"
    a_draft.status = "draft"
    a_draft.save()

    a_last = Article()
    a_last.slug = "article-last"
    a_last.title = "Article last"
    a_last.status = "published"
    a_last.save()

    return [valid_article(), a2, del_a2, a_draft, a_last]


@pytest.fixture
def applications_list():
    app2 = Application()
    app2.title = "Second application"
    app2.slug = "app2"
    app2.url = "http://second.app.com"
    app2.status = 'published'
    app2.save()

    del_app = Application()
    del_app.title = "Deleted application"
    del_app.slug = "app-del"
    del_app.url = "http://deleted.app.com"
    del_app.status = 'published'
    del_app.save()
    del_app.delete()

    app_last = Application()
    app_last.title = "Last application"
    app_last.slug = "app-last"
    app_last.url = "http://last.app.com"
    app_last.status = 'published'
    app_last.save()

    return [valid_application(), app2, del_app, app_last]


@pytest.fixture
def valid_application():
    a = Application()
    a.slug = "test-name"
    a.title = "Test name"
    a.notes = "Treść"
    a.url = "http://smth.smwheere.com"
    a.status = 'published'
    a.save()
    return a


@pytest.fixture
def unsave_application():
    a = Application()
    a.slug = "test-name"
    a.title = "Test name"
    a.url = "http://smth.smwheere.com"
    return a


@pytest.fixture
def valid_article():
    a = Article()
    a.slug = "test-name"
    a.title = "Test name"
    a.save()
    return a


@pytest.fixture
def draft_article():
    a = Article()
    a.slug = "draft"
    a.title = "Draft"
    a.status = 'draft'
    a.save()
    return a


@pytest.fixture
def unsave_article():
    a = Article()
    a.slug = "test-name"
    a.title = "Test name"
    return a


@pytest.fixture
def valid_dataset(valid_organization):
    a = Dataset()
    a.slug = "test-dataset-name"
    a.title = "test name"
    a.organization = valid_organization
    a.save()
    return a


@pytest.fixture
def valid_dataset2(valid_organization):
    a = Dataset()
    a.slug = "test-dataset-name2"
    a.title = "test name2"
    a.organization = valid_organization
    a.save()
    return a


@pytest.fixture
def dataset_org2(valid_organization2):
    a = Dataset()
    a.slug = "to-kill"
    a.title = "Zlecenia zabójstw"
    a.organization = valid_organization2
    a.save()
    return a


@pytest.fixture
def dataset_list(valid_dataset, valid_dataset2, dataset_org2):
    return [valid_dataset2, dataset_org2, valid_dataset]


@pytest.fixture
def valid_tag():
    tag = Tag()
    tag.name = "test"
    tag.save()
    return tag


@pytest.fixture
def valid_resource(valid_dataset):
    resource = Resource()
    resource.url = "http://smth.smwhere.com"
    resource.title = "Resource name"
    resource.resource_type = "Table"
    resource.dataset = valid_dataset
    resource.save()
    return resource


@pytest.fixture
def valid_resource_with_description(valid_dataset):
    resource = Resource()
    resource.url = "http://smth.smwhere.com"
    resource.title = "Resource name"
    resource.description = "Test Resource Description"
    resource.dataset = valid_dataset
    resource.status = 'published'
    resource.save()
    return resource


@pytest.fixture
def valid_resource2(valid_dataset2):
    resource = Resource()
    resource.url = "http://smth.smwhere.com"
    resource.title = "Resource name2"
    resource.resource_type = "Table"
    resource.dataset = valid_dataset2
    resource.save()
    return resource


@pytest.fixture
def resource_without_dataset(valid_dataset):
    resource = Resource()
    resource.url = "http://smth.smwhere.com"
    resource.title = "Resource name"
    resource.is_external = True
    resource.resource_type = "Table"
    # resource.dataset = valid_dataset
    resource.save()
    return resource


@pytest.fixture
def resource_in_dataset_org2(dataset_org2):
    resource = Resource()
    resource.url = "http://tokill.shadowthieves.bg/cowled_wizards"
    resource.title = "Zakapturzeni czarodzieje"
    resource.resource_type = "Table"
    resource.dataset = dataset_org2
    resource.save()
    return resource


@pytest.fixture
def resource_list(valid_resource, valid_resource_with_description, valid_resource2,
                  resource_in_dataset_org2):
    return [
        valid_resource2,
        valid_resource_with_description,
        resource_in_dataset_org2,
        valid_resource,
    ]


@pytest.fixture
def valid_category():
    category = Category()
    category.slug = "Category name"
    category.save()
    return category


@pytest.fixture
def es_dsl_queryset():
    return elasticsearch_dsl.Search()


@pytest.fixture()
def fake_user():
    return namedtuple('User', 'email state fullname')


@pytest.fixture()
def fake_session():
    return namedtuple('Session', 'session_key')
