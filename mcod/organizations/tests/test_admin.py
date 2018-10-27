import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_deleted_dataset_not_in_inlines(valid_dataset, valid_organization, admin_user):
    assert valid_dataset.organization == valid_organization
    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse("admin:organizations_organization_change", args=[valid_organization.id]))
    assert valid_dataset.title in str(response.content)
    valid_dataset.delete()
    assert valid_dataset.is_removed is True
    client = Client()
    client.force_login(admin_user)
    response = client.get(reverse("admin:organizations_organization_change", args=[valid_organization.id]))
    assert valid_dataset.slug not in str(response.content)
    client = Client()
    client.force_login(admin_user)
    response = client.get("/datasets/dataset")
    assert valid_dataset.slug not in str(response.content)
