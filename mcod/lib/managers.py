from django.db import models
from django.db.models.query import QuerySet
from django.db.models.signals import post_save


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_removed=True)


class SoftDeletableQuerySet(QuerySet):
    def delete(self):
        for obj in self:
            post_save.send(self, instance=obj, qs_delete=True)
        self.update(is_removed=True)


class SoftDeletableManager(models.Manager):
    _queryset_class = SoftDeletableQuerySet

    def get_queryset(self):
        kwargs = {'model': self.model, 'using': self._db}
        if hasattr(self, '_hints'):
            kwargs['hints'] = self._hints

        return self._queryset_class(**kwargs).filter(is_removed=False)
