from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.

class License(models.Model):
    name = models.CharField(max_length=200, verbose_name=_('Name'))
    title = models.CharField(max_length=250, verbose_name=_('Title'))
    url = models.URLField(blank=True, null=True, verbose_name=_('URL'))

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('License')
        verbose_name_plural = _('Licenses')

    @classmethod
    def accusative_case(cls):
        return _("acc: License")
