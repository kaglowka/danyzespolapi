from django.db import models


class IndexableMixin(object):
    @property
    def is_indexable(self):
        return True


class CounterMixin(models.Model):
    views_count = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True
