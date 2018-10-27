from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ApplicationsConfig(AppConfig):
    name = 'mcod.applications'
    verbose_name = _('Applications')
