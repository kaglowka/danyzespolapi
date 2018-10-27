from django.db import models
from django_elasticsearch_dsl.signals import BaseSignalProcessor

from mcod.lib.search.tasks import delete_document, pre_delete_document, delete_with_related, update_with_related


class AsyncSignalProcessor(BaseSignalProcessor):
    def setup(self):
        models.signals.post_save.connect(self.handle_save)
        models.signals.post_delete.connect(self.handle_delete)

        models.signals.m2m_changed.connect(self.handle_m2m_changed)
        models.signals.pre_delete.connect(self.handle_pre_delete)

    def teardown(self):
        models.signals.post_save.disconnect(self.handle_save)
        models.signals.post_delete.disconnect(self.handle_delete)
        models.signals.m2m_changed.disconnect(self.handle_m2m_changed)
        models.signals.pre_delete.disconnect(self.handle_pre_delete)

    def handle_save(self, sender, instance, **kwargs):
        is_indexable = getattr(instance, 'is_indexable', False)
        if is_indexable:
            should_delete = (hasattr(instance, 'is_removed') and instance.is_removed) or (
                    hasattr(instance, 'status') and instance.status != 'published') or \
                    kwargs.get('qs_delete', False)
            if should_delete:
                delete_with_related.apply_async(
                    args=(instance._meta.app_label, instance._meta.object_name, instance.id), countdown=2)
            else:

                if instance._meta.proxy:
                    object_name = instance._meta.concrete_model._meta.object_name
                else:
                    object_name = instance._meta.object_name

                update_with_related.apply_async(
                    args=(instance._meta.app_label, object_name, instance.id), countdown=2)

    def handle_pre_delete(self, sender, instance, **kwargs):
        is_indexable = getattr(instance, 'is_indexable', False)
        if is_indexable:
            pre_delete_document.apply_async(args=(instance._meta.app_label, instance._meta.object_name, instance.id),
                                            countdown=2)

    def handle_delete(self, sender, instance, **kwargs):
        is_indexable = getattr(instance, 'is_indexable', False)
        if is_indexable:
            delete_document.apply_async(args=(instance._meta.app_label, instance._meta.object_name, instance.id),
                                        countdown=2)

    def handle_m2m_changed(self, sender, instance, action, **kwargs):
        if action in ('post_add', 'post_remove', 'post_clear'):
            self.handle_save(sender, instance)
        elif action in ('pre_remove', 'pre_clear'):
            self.handle_pre_delete(sender, instance)
