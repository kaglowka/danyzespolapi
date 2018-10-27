import pytest
import re
from django.test import Client
from django.urls import reverse


@pytest.mark.django_db
def test_admin_shouldnt_see_deleted_resources(valid_resource, admin_user):
    client = Client()
    client.force_login(admin_user)
    response = client.get("/resources/resource/", follow=True)
    assert valid_resource.title in str(response.content)
    valid_resource.delete()
    assert valid_resource.is_removed is True
    client = Client()
    client.force_login(admin_user)
    response = client.get("/resources/resource/", follow=True)
    assert valid_resource.title not in str(response.content)


@pytest.mark.django_db
def test_editor_shouldnt_see_deleted_resources(valid_resource, admin_user, editor_user):
    client = Client()
    client.force_login(admin_user)
    response = client.get("/resources/resource/", follow=True)
    assert valid_resource.title in str(response.content)
    title = valid_resource.title
    valid_resource.delete()
    assert valid_resource.is_removed is True
    client = Client()
    editor_user.organizations.set([valid_resource.dataset.organization])
    editor_user.save()
    client.force_login(editor_user)
    response = client.get("/resources/resource/", follow=True)
    assert title not in str(response.content)


@pytest.mark.django_db
def test_admin_can_add_resource_based_on_other_resource(valid_resource_with_description, admin_user, valid_dataset):
    res = valid_resource_with_description

    id_ = res.id
    client = Client()
    client.force_login(admin_user)
    response = client.get(f"/resources/resource/{id_}", follow=True)
    assert response.status_code == 200
    assert '<a href="/resources/resource/add/?from_id={}" class="btn btn-high" id="duplicate_button">'.format(
        id_) in str(
        response.content)
    response = client.get(f"/resources/resource/add/?from_id={id_}")
    assert response.status_code == 200
    content = response.content.decode()

    # is form filled with proper data
    assert res.title in content
    assert res.description in content
    assert res.status in content
    assert valid_dataset.title in content


@pytest.mark.django_db
def test_editor_can_add_resource_based_on_other_resource(valid_resource_with_description, user_with_organization,
                                                         valid_dataset):
    res = valid_resource_with_description

    id_ = res.id
    client = Client()
    client.force_login(user_with_organization)
    response = client.get(f"/resources/resource/{id_}", follow=True)
    assert response.status_code == 200
    assert '<a href="/resources/resource/add/?from_id={}" class="btn btn-high" id="duplicate_button">'.format(
        id_) in str(
        response.content)
    response = client.get(f"/resources/resource/add/?from_id={id_}")
    assert response.status_code == 200
    content = response.content.decode()

    # is form filled with proper data
    assert res.title in content
    assert res.description in content
    assert res.status in content
    assert valid_dataset.title in content


@pytest.mark.django_db
def test_editor_not_in_organization_cant_see_resource_from_organizaton(valid_resource_with_description, editor_user,
                                                                       valid_dataset):
    res = valid_resource_with_description
    id_ = res.id
    client = Client()
    client.force_login(editor_user)
    response = client.get(f"/resources/resource/{id_}", follow=True)
    assert response.status_code == 403


@pytest.mark.django_db
def test_new_resource_cant_be_duplicated(valid_resource_with_description, user_with_organization):
    res = valid_resource_with_description

    id_ = res.id
    client = Client()
    client.force_login(user_with_organization)
    response = client.get(f"/resources/resource/add/", follow=True)
    assert response.status_code == 200
    assert '<a href="/resources/resource/add/?from_id={}" class="btn" id="duplicate_button">'.format(id_) not in str(
        response.content)


@pytest.mark.django_db
def test_trash_for_editor(resource_list, user_with_organization):
    resource_list[0].delete()
    resource_list[2].delete()

    client = Client()
    client.force_login(user_with_organization)
    response = client.get(reverse("admin:resources_trash_changelist"))
    pattern = re.compile(r"/resources/trash/\d+/change")
    result = pattern.findall(str(response.content))
    assert result == [f'/resources/trash/{resource_list[0].id}/change']

    resource_list[1].delete()
    resource_list[3].delete()
    response = client.get(reverse("admin:resources_trash_changelist"))
    result = pattern.findall(str(response.content))
    resources = set(f'/resources/trash/{res.id}/change'
                    for res in resource_list
                    if res.dataset.organization in user_with_organization.organizations.all())
    assert set(result) == resources
