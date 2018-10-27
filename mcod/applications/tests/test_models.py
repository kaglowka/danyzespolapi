import pytest
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.test import Client
from django.conf import settings
from datetime import date
from mcod.applications.models import Application
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestApplicationModel(object):
    def test_can_not_create_empty_application(self):
        with pytest.raises(ValidationError)as e:
            a = Application()
            a.full_clean()
        assert "'slug'" in str(e.value)
        assert "'title'" in str(e.value)
        assert "'url'" in str(e.value)
        assert "'notes'" in str(e.value)
        # assert "'status'" in str(e.value)

    def test_create_application(self):
        a = Application()
        a.slug = "test-name"
        a.title = "Test name"
        a.notes = "Treść"
        a.url = "http://smth.smwheere.com"
        # a.status = 'active'
        assert a.full_clean() is None
        assert a.id is None
        a.save()
        assert a.id is not None
        assert a.status == "published"

    # def test_get_url_path(self, valid_application):
    #     assert valid_application.get_url_path() == '/pl/applications/application/%s/change/' % valid_application.id
    #
    # def test_get_url_path_no_reverse_match(self, unsave_application):
    #     assert unsave_application.get_url_path() == ''
    #
    # def test_get_photo_application_without_photo(self, valid_application):
    #     assert valid_application.get_photo() == ""
    #
    # def test_get_photo(self, valid_application):
    #     today = date.today().isoformat().replace('-', '')
    #     valid_application.image = "some_image.jpg"
    #     expected = """<a href="/pl/applications/application/%s/change/" target="_blank">
    #         <img src="/media/images/applications/%s/some_image.jpg" alt="" width="100" />
    #         </a>""" % (valid_application.id, today)
    #
    #     result = valid_application.get_photo()
    #     assert expected == result

    def test_add_dataset(self, valid_application, valid_dataset):
        valid_application.datasets.set([valid_dataset])
        assert valid_application.full_clean() is None
        valid_application.save()
        app = Application.objects.get(id=valid_application.id)
        assert valid_dataset in app.datasets.all()

    def test_add_dataset_twice(self, valid_application, valid_dataset):
        valid_application.datasets.set([valid_dataset])
        assert valid_application.full_clean() is None
        valid_application.save()
        app = Application.objects.get(id=valid_application.id)
        assert valid_dataset in app.datasets.all()
        assert len(app.datasets.all()) == 1
        valid_application.datasets.add(valid_dataset)
        assert valid_application.full_clean() is None
        valid_application.save()
        assert valid_dataset in app.datasets.all()
        assert len(app.datasets.all()) == 1

    def test_add_tag(self, valid_application, valid_tag):
        valid_application.tags.set([valid_tag])
        assert valid_application.full_clean() is None
        valid_application.save()
        app = Application.objects.get(id=valid_application.id)
        assert valid_tag in app.tags.all()

    def test_application_has_proper_columns_and_relations(self, valid_application):
        app_dict = valid_application.__dict__
        fields = [
            "id",
            "slug",
            "title",
            "notes",
            "author",
            "status",
            "modified",
            "created_by_id",
            "image",
            "created",
            "url",
        ]
        for f in fields:
            assert f in app_dict
        assert isinstance(valid_application.datasets.all(), QuerySet)
        assert isinstance(valid_application.tags.all(), QuerySet)

    def test_validate_name_uniqness(self, valid_application):
        app = Application()
        app.slug = valid_application.slug

        with pytest.raises(ValidationError) as e:
            app.full_clean()

        assert "'slug': " in str(e.value)

    def test_safe_delete(self, valid_application):
        assert valid_application.status == 'published'
        valid_application.delete()
        assert valid_application.is_removed is True
        with pytest.raises(ObjectDoesNotExist) as e:
            Application.objects.get(id=valid_application.id)
        assert "Application matching query does not exist." in str(e.value)
        assert Application.raw.get(id=valid_application.id)

    def test_unsafe_delete(self, valid_application):
        assert valid_application.status == 'published'
        valid_application.delete(soft=False)
        # assert valid_application.status == 'deleted'
        with pytest.raises(ObjectDoesNotExist) as e:
            Application.objects.get(id=valid_application.id)
        assert "Application matching query does not exist." in str(e.value)

    def test_image_path_and_url(self, valid_application):
        assert not valid_application.image
        valid_application.image = SimpleUploadedFile("somefile.jpg", b"""1px""")
        valid_application.save()
        assert valid_application.image
        date_folder = date.today().isoformat().replace('-', '')
        image_name = valid_application.image.name
        assert valid_application.image.url == f"/test/media/images/applications/{image_name}"
        assert valid_application.image.path == f"{settings.IMAGES_MEDIA_ROOT}/applications/{image_name}"
        assert date_folder in valid_application.image.url
        assert date_folder in valid_application.image.path


@pytest.mark.django_db
class TestApplicationUserRoles(object):
    def test_editor_doesnt_see_applications_in_admin_panel(self, editor_user):
        client = Client()
        client.login(email=editor_user.email, password="P4n.Samochodzik:)")
        response = client.get("/")
        assert response.status_code == 200
        assert '/applications/' not in str(response.content)

    def test_editor_cant_go_to_applications_in_admin_panel(self, editor_user):
        client = Client()
        client.login(email=editor_user.email, password="P4n.Samochodzik:)")
        response = client.get("/applications/")
        assert response.status_code == 404

    def test_admin_see_applications_in_admin_panel(self, admin_user):
        client = Client()
        client.login(email=admin_user.email, password="P4n.Samochodzik:)")
        response = client.get("/")
        assert response.status_code == 200
        assert '/applications/' in str(response.content)

    def test_admin_can_go_to_applications_in_admin_panel(self, admin_user):
        client = Client()
        client.login(email=admin_user.email, password="P4n.Samochodzik:)")
        response = client.get("/applications/")
        assert response.status_code == 200
