from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from functools import wraps
from model_utils.fields import AutoCreatedField, AutoLastModifiedField

from mcod.lib.managers import SoftDeletableManager


class AutoLastModifiedField(AutoLastModifiedField):
    """
        Change models_utils AutoLastModifiedField.
        When model_instance.soft_update = True - save old value instead of now()

    """

    def pre_save(self, model_instance, add):
        soft_update = False
        if hasattr(model_instance, 'soft_update'):
            soft_update = model_instance.soft_update

        if add and hasattr(model_instance, self.attname) or soft_update:
            # when creating an instance and the modified date is set
            # don't change the value, assume the developer wants that
            # control.
            value = getattr(model_instance, self.attname)
        else:
            value = now()
            setattr(model_instance, self.attname, value)
        return value


class TimeStampedModel(models.Model):
    """
    An abstract base class model that provides self-updating
    ``created`` and ``modified`` fields.

    """
    soft_update = False
    created = AutoCreatedField(_('created'))
    modified = AutoLastModifiedField(_('modified'))

    class Meta:
        abstract = True


class SoftDeletableModel(models.Model):
    is_removed = models.BooleanField(default=False)

    class Meta:
        abstract = True

    objects = SoftDeletableManager()

    def delete(self, using=None, soft=True, *args, **kwargs):
        if soft:
            self.is_removed = True
            self.save(using=using)
        else:
            return super().delete(using=using, *args, **kwargs)


def skip_signal():
    def _skip_signal(signal_func):
        @wraps(signal_func)
        def _decorator(sender, instance, **kwargs):
            if hasattr(instance, 'skip_signal'):
                if instance.skip_signal:
                    return None
            return signal_func(sender, instance, **kwargs)

        return _decorator

    return _skip_signal
