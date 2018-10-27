# from datetime import date
#
# import pytest
# from django.conf import settings
# from django.core.exceptions import ObjectDoesNotExist
# from django.core.files.uploadedfile import SimpleUploadedFile
# from mcod.resources.models import Resource

# TODO: To be refactored
# @pytest.mark.django_db
# class TestResourceModel(object):
#     def test_resource_fields(self, valid_resource):
#         r_dict = valid_resource.__dict__
#         fields = [
#             "uuid",
#             "file",
#             "format",
#             "description",
#             "position",
#             "old_customfields",
#             "title",
#             "id",
#             "dataset_id",
#             "link",
#             "is_removed",
#             "created",
#             "modified",
#             "status",
#             "modified_by_id",
#             "created_by_id",
#         ]
#
#         for f in fields:
#             assert f in r_dict
#
#     def test_resource_create(self, valid_dataset):
#         r = Resource()
#         # r.name = "test"
#         r.title = "test"
#         r.description = "Opis zasobu"
#         r.format = "csv"
#         r.resource_type = "zestawienie"
#         r.dataset = valid_dataset
#         assert r.full_clean() is None
#         assert r.id is None
#         r.link = "http://test.to.resource.pl/1.xls"
#         r.save()
#         assert r.id is not None
#
#     def test_resource_safe_delete(self, valid_resource):
#         assert valid_resource.status == 'published'
#         valid_resource.delete()
#         assert valid_resource.is_removed is True
#         assert Resource.deleted.get(id=valid_resource.id)
#         assert Resource.raw.get(id=valid_resource.id)
#         with pytest.raises(ObjectDoesNotExist):
#             Resource.objects.get(id=valid_resource.id)
#
#     def test_resource_unsafe_delete(self, valid_resource):
#         assert valid_resource.status == 'published'
#         valid_resource.delete(soft=False)
#         with pytest.raises(ObjectDoesNotExist):
#             Resource.raw.get(id=valid_resource.id)
#         with pytest.raises(ObjectDoesNotExist):
#             Resource.deleted.get(id=valid_resource.id)
#
#     def test_file_url_and_path(self, valid_resource):
#         assert not valid_resource.file
#         valid_resource.file = SimpleUploadedFile("somefile.jpg", b"""1px""")
#         valid_resource.save()
#         assert valid_resource.file
#         date_folder = date.today().isoformat().replace('-', '')
#         file_name = valid_resource.file.name
#         assert valid_resource.file.url == f"/test/media/resources/{file_name}"
#         assert valid_resource.file.path == f"{settings.RESOURCES_MEDIA_ROOT}/{file_name}"
#         assert date_folder in valid_resource.file.url
#         assert date_folder in valid_resource.file.path
