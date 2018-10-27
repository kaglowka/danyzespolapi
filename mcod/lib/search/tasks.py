from celery import shared_task
from celery.utils.log import get_task_logger
from django.apps import apps
from django_elasticsearch_dsl.registries import registry

logger = get_task_logger('index_tasks')


def _instance(app_label, object_name, instance_id):
    model = apps.get_model(app_label, object_name)
    if hasattr(model, 'raw'):
        instance = model.raw.get(pk=instance_id)
    else:
        instance = model.objects.get(pk=instance_id)

    return instance


@shared_task
def update_document(app_label, object_name, instance_id):
    instance = _instance(app_label, object_name, instance_id)
    registry.update(instance)
    return {
        'app': app_label,
        'model': object_name,
        'instance_id': instance_id
    }


@shared_task
def update_with_related(app_label, object_name, instance_id):
    instance = _instance(app_label, object_name, instance_id)
    registry.update(instance)
    registry.update_related(instance)
    return {
        'app': app_label,
        'model': object_name,
        'instance_id': instance_id
    }


@shared_task
def delete_document(app_label, object_name, instance_id):
    instance = _instance(app_label, object_name, instance_id)
    registry.delete(instance, raise_on_error=False)
    return {
        'app': app_label,
        'model': object_name,
        'instance_id': instance_id
    }


@shared_task
def delete_with_related(app_label, object_name, instance_id):
    instance = _instance(app_label, object_name, instance_id)
    registry.delete_related(instance)
    registry.delete(instance, raise_on_error=False)
    return {
        'app': app_label,
        'model': object_name,
        'instance_id': instance_id
    }


@shared_task
def pre_delete_document(app_label, object_name, instance_id):
    instance = _instance(app_label, object_name, instance_id)
    registry.delete_related(instance)
    return {
        'app': app_label,
        'model': object_name,
        'instance_id': instance_id
    }
