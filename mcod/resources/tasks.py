import json

from celery import shared_task
from django.apps import apps


@shared_task
def get_resource_from_url(resource_id, update_file=True):
    Resource = apps.get_model('resources', 'Resource')
    resource = Resource.raw.get(id=resource_id)

    if update_file:
        resource.update_from_link()
        resource.raw_save()
        if resource.type == 'file':
            process_resource_file.apply_async(args=(resource.id, False), countdown=2)

    result = {
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type
    }

    if resource.type == 'file' and resource.file:
        result['path'] = resource.file.path
        result['url'] = resource.file_url

    return json.dumps(result)


@shared_task
def process_resource_file(resource_id, update_link=True):
    Resource = apps.get_model('resources', 'Resource')
    resource = Resource.raw.get(id=resource_id)
    resource.update_from_file(update_link=update_link)
    resource.raw_save()
    resource.index_data()
    if update_link:
        get_resource_from_url.apply_async(args=(resource_id, False), countdown=2)
    return json.dumps({
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type,
        'path': resource.file.path,
        'url': resource.file_url
    })


@shared_task
def process_file_data(resource_id):
    Resource = apps.get_model('resources', 'Resource')
    resource = Resource.raw.get(id=resource_id)
    resource._process_data()

    return json.dumps({
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type,
        'path': resource.file.path,
        'url': resource.file_url
    })
