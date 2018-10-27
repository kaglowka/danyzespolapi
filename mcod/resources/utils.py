from django.apps import apps
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from mcod.lib.utils import validate_file_data


def verify_file(resource_id):
    Resource = apps.get_model('resources', 'Resource')
    try:
        resource = Resource.raw.get(pk=resource_id)
    except Resource.DoesNotExist:
        raise ValidationError(_('Resource with id %s does not exist' % resource_id))

    if not resource.file:
        raise ValidationError(_('No file attached to resource with id %s' % resource_id))

    try:
        f = resource.file.file
    except FileNotFoundError:
        raise ValidationError(_('File %s does not exist, please upload it again') % resource.file.name)

    report = validate_file_data(f, ignore_blank_headers=True)

    return report
