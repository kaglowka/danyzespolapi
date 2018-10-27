import json
import uuid
import logging
import magic
import os
from celery.signals import task_prerun, task_failure, task_success
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, post_init, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult
from elasticsearch_dsl.connections import Connections
from goodtables import validate
from mimeparse import parse_mime_type
from model_utils import Choices
from model_utils.models import StatusModel
from tableschema import Table

from mcod.histories.models import History
from mcod.lib import storages
from mcod.lib.managers import DeletedManager, SoftDeletableManager
from mcod.lib.model_mixins import CounterMixin, IndexableMixin
from mcod.lib.model_utils import TimeStampedModel, SoftDeletableModel
from mcod.lib.search.storage import ElasticsearchStorage
from mcod.lib.utils import download_file, analyze_resource_file, content_type_from_file_format
from mcod.resources.tasks import get_resource_from_url, process_resource_file, process_file_data

rfp = logging.getLogger('resource_file_processing')

User = get_user_model()

es_connections = Connections()
es_connections.configure(**settings.ELASTICSEARCH_DSL)

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft'))
]

OPENNESS_SCORE = {_type: os for _, _type, _, os in settings.SUPPORTED_CONTENT_TYPES}


class ResourceDataValidationError(Exception):
    pass


def supported_formats_choices():
    data = []
    for item in settings.SUPPORTED_CONTENT_TYPES:
        data.extend(item[2])

    return [(i, i.upper()) for i in sorted(list(set(data)))]


@deconstructible
class FileValidator(object):
    error_messages = {
        'max_size': ("Ensure this file size is not greater than %(max_size)s."
                     " Your file size is %(size)s."),
        'min_size': ("Ensure this file size is not less than %(min_size)s. "
                     "Your file size is %(size)s."),
        'content_type': "Files of type %(content_type)s are not supported.",
    }

    def __call__(self, file):
        min_size = settings.RESOURCE_MIN_FILE_SIZE
        max_size = settings.RESOURCE_MAX_FILE_SIZE
        try:
            filesize = file.size
        except FileNotFoundError:
            raise ValidationError(_('File %s does not exist, please upload it again') % file.name)

        if max_size is not None and filesize > max_size:
            params = {
                'max_size': filesizeformat(max_size),
                'size': filesizeformat(filesize),
            }
            raise ValidationError(self.error_messages['max_size'],
                                  'max_size', params)

        if min_size is not None and filesize < min_size:
            params = {
                'min_size': filesizeformat(min_size),
                'size': filesizeformat(filesize)
            }
            raise ValidationError(self.error_messages['min_size'],
                                  'min_size', params)

        mime_type = magic.from_buffer(file.read(), mime=True)
        family, content_type, options = parse_mime_type(mime_type)
        file.seek(0)
        if content_type not in [ct[1] for ct in settings.SUPPORTED_CONTENT_TYPES]:
            params = {'content_type': content_type}
            raise ValidationError(self.error_messages['content_type'],
                                  'content_type', params)

    def __eq__(self, other):
        return isinstance(other, FileValidator)


RESOURCE_TYPE = (
    ('file', _('File')),
    ('website', _('Web Site')),
    ('api', _('API')),
)


class Resource(CounterMixin, IndexableMixin, StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4)
    file = models.FileField(verbose_name=_("File"), storage=storages.get_storage('resources'),
                            upload_to='%Y%m%d',
                            max_length=2000, blank=True, null=True)
    file_info = models.TextField(blank=True, null=True, editable=False, verbose_name=_("File info"))
    file_encoding = models.CharField(max_length=150, null=True, blank=True, editable=False,
                                     verbose_name=_("File encoding"))
    link = models.URLField(verbose_name=_('Resource Link'), max_length=2000, blank=True, null=True)
    title = models.CharField(max_length=500, verbose_name=_("title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    position = models.IntegerField(default=1, verbose_name=_("Position"))
    dataset = models.ForeignKey('datasets.Dataset', on_delete=models.CASCADE, related_name='resources',
                                verbose_name=_('Dataset'))

    format = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("Format"),
                              choices=supported_formats_choices())
    type = models.CharField(max_length=10, choices=RESOURCE_TYPE, default='file', editable=False,
                            verbose_name=_("Type"))

    openness_score = models.IntegerField(default=0, verbose_name=_("Openness score"),
                                         validators=[MinValueValidator(0), MaxValueValidator(5)])

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='resources_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='resources_modified'
    )
    link_tasks = models.ManyToManyField('django_celery_results.TaskResult', verbose_name=_('Download Tasks'),
                                        blank=True,
                                        related_name='link_task_resources',
                                        )
    file_tasks = models.ManyToManyField('django_celery_results.TaskResult', verbose_name=_('Download Tasks'),
                                        blank=True,
                                        related_name='file_task_resources')
    data_tasks = models.ManyToManyField('django_celery_results.TaskResult', verbose_name=_('Download Tasks'),
                                        blank=True,
                                        related_name='data_task_resources')

    old_file = models.FileField(verbose_name=_("File"), storage=storages.get_storage('resources'), upload_to='',
                                max_length=2000, blank=True, null=True)
    old_resource_type = models.TextField(verbose_name=_("Data type"), null=True)
    old_format = models.CharField(max_length=150, blank=True, null=True, verbose_name=_("Format"))
    old_customfields = JSONField(blank=True, null=True, verbose_name=_("Customfields"))
    old_link = models.URLField(verbose_name=_('Resource Link'), max_length=2000, blank=True, null=True)
    downloads_count = models.PositiveIntegerField(default=0)

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    _data = None

    class Meta:
        verbose_name = _("Resource")
        verbose_name_plural = _("Resources")
        db_table = 'resource'
        default_manager_name = "objects"

    class Data:
        def __init__(self, resource):
            self.resource = resource
            self.storage = ElasticsearchStorage(es_connections.get_connection())

        def get_file_info(self):
            return self.resource.file.path, {
                'format': self.resource.format,
                'encoding': self.resource.file_encoding or 'utf-8'
            }

        def reindex(self):
            file_path, params = self.get_file_info()
            t = Table(file_path, ignore_blank_headers=True, **params)
            schema = t.infer()
            data = t.iter(keyed=True)
            self.storage.create(self.index_name, schema, reindex=True, always_recreate=True)
            self.storage.write(self.index_name, data)
            for res in self.storage.write(self.index_name, data):
                pass

        def get_source(self, mode=None):
            if mode == 'file':
                return self.resource.file.path, {
                    'format': self.resource.format,
                    'encoding': self.resource.file_encoding or 'utf-8'
                }
            else:
                return self.storage.read(self.index_name), {}

        def validate(self):
            report = validate(self.resource.file.path, error_limit=10, format=self.resource.format,
                              encoding=self.resource.file_encoding,
                              ignore_blank_headers=True)
            if not report['valid']:
                raise ResourceDataValidationError(report['tables'][0]['errors'])

            return report

        @property
        def data(self):
            source = self.storage.read(self.index_name)
            t = Table(source, ignore_blank_headers=True)
            return (t.infer(), t.headers, t.read(keyed=False, limit=1000))

        @property
        def index_name(self):
            return 'resource_%s' % self.resource.id

    def __str__(self):
        return self.title

    @property
    def file_changed(self):
        old_file_name = getattr(self, '_orig_file_name', None)
        new_file_name = None if not self.file else id(self.file.name)
        old_file_size = getattr(self, '_orig_file_size', None)
        try:
            new_file_size = None if not self.file else id(self.file.size)
        except FileNotFoundError:
            new_file_size = None
        result = old_file_name != new_file_name and old_file_size != new_file_size
        if result:
            rfp.info('(%i) File changed.', self.id)
            rfp.info('(%i) Old file name: %s, new file name: %s.', self.id, old_file_name, new_file_name)
            rfp.info('(%i) Old file size: %s, new file size: %s.', self.id, old_file_size, new_file_size)
        return result

    @property
    def link_changed(self):
        if hasattr(self, '_orig_link'):
            result = getattr(self, '_orig_link') != self.link
            if result:
                rfp.info('(%i) Link changed.', self.id)
                rfp.info('(%i) Old link: %s, new link: %s.', self.id, self._orig_link, self.link)
            return result
        return False

    @property
    def link_is_valid(self):
        task = self.link_tasks.last()
        return task.status if task else 'NOT_AVAILABLE'

    @property
    def file_is_valid(self):
        task = self.file_tasks.last()
        return task.status if task else 'NOT_AVAILABLE'

    @property
    def data_is_valid(self):
        task = self.data_tasks.last()
        return task.status if task else 'NOT_AVAILABLE'

    @property
    def file_url(self):
        return '' if not self.file else '%s%s' % (settings.BASE_URL, self.file.url)

    @property
    def is_indexable(self):
        if self.type == 'file' and not self.file_is_valid:
            return False

        if self.type in ('api', 'website') and not self.link_is_valid:
            return False

        return True

    @property
    def data(self):
        if not self._data:
            if self.format in ('csv', 'tsv', 'xls', 'xlsx', 'ods') and self.file:
                self._data = self.Data(self)
        return self._data

    def index_data(self):
        if not self.file:
            return False

        if self.format not in ('csv', 'tsv', 'xls', 'xlsx', 'ods'):
            return False

        process_file_data.apply_async(args=[self.id, ], countdown=2)

    def _process_data(self):
        self.data.validate()
        self.data.reindex()

    def rollback_to_latest_version(self):
        # TODO: this is very slow
        history = History.objects.filter(table_name='resources', row_id=self.pk).last()
        if history:
            for attr, value in history.old_value.items():
                setattr(self, attr, value)
            self.raw_save()
            return True
        return False

    def update_from_link(self):
        resource_type, options = download_file(self.link)

        if resource_type == 'file':
            filename = options['filename']
            if filename:
                self.file.name = self.save_file(options['content'], options['filename'])
                self.format = options['format']
        else:  # API or WWW
            self.type = resource_type
            self.format = options['format']
            # There's no file for this resource_type
            self.file = None
            self.file_info = None
            self.file_encoding = None

        self.openness_score = self._openness_score if self.format else 0

    def raw_save(self):
        self.soft_update = True
        self.skip_async_tasks = True
        self.save()

    def save_file(self, content, filename):
        dt = self.created.date() if self.created else now().date()
        subdir = dt.isoformat().replace("-", "")
        dest_dir = os.path.join(self.file.storage.location, subdir)
        os.makedirs(dest_dir, exist_ok=True)
        file_path = os.path.join(dest_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(content.read())
        return '%s/%s' % (subdir, filename)

    def update_from_file(self, update_link=True):
        self.format, self.file_info, self.file_encoding = analyze_resource_file(self.file.file.name)
        self.type = 'file'
        if update_link:
            self.link = self.file_url
        self.openness_score = self._openness_score if self.format else 0

    @classmethod
    def accusative_case(cls):
        return _("acc: Resource")

    @property
    def _openness_score(self):
        if not self.format:
            return 0
        _, content = content_type_from_file_format(self.format.lower())
        return OPENNESS_SCORE.get(content, 0)


@receiver(post_init, sender=Resource)
def store_orig_values(sender, instance, *args, **kwargs):
    file_name, file_size = None, None
    if instance.file:
        try:
            file_name = instance.file.name
            file_size = instance.file.size
        except FileNotFoundError:
            pass

    instance._orig_file_name = file_name
    instance._orig_file_size = file_size
    instance._orig_link = instance.link


@receiver(pre_save, sender=Resource)
def preprocess_resource(sender, instance, *args, **kwargs):
    if not instance.soft_update:
        instance.openness_score = instance._openness_score


@receiver(post_save, sender=Resource)
def process_resource(sender, instance, *args, **kwargs):
    if not instance.is_removed:
        skip_async_tasks = getattr(instance, 'skip_async_tasks', False)
        if not skip_async_tasks:
            if instance.link_changed:
                get_resource_from_url.apply_async(args=[instance.id, ], countdown=2)
            elif instance.file_changed:
                process_resource_file.apply_async(args=[instance.id, ], countdown=2)


@task_prerun.connect(sender=get_resource_from_url)
def append_link_task(sender, task_id, task, signal, **kwargs):
    try:
        resource_id = int(kwargs['args'][0])
        resource = Resource.objects.get(pk=resource_id)
        result_task = TaskResult.objects.get_task(task_id)
        result_task.save()
        resource.link_tasks.add(result_task)
    except Exception:
        # TODO: log this exception
        pass


@task_prerun.connect(sender=process_resource_file)
def append_file_task(sender, task_id, task, signal, **kwargs):
    try:
        resource_id = int(kwargs['args'][0])
        resource = Resource.objects.get(pk=resource_id)
        result_task = TaskResult.objects.get_task(task_id)
        result_task.save()
        resource.file_tasks.add(result_task)
    except Exception:
        # TODO: log this exception
        pass


@task_prerun.connect(sender=process_file_data)
def append_data_task(sender, task_id, task, signal, **kwargs):
    try:
        resource_id = int(kwargs['args'][0])
        resource = Resource.objects.get(pk=resource_id)
        result_task = TaskResult.objects.get_task(task_id)
        result_task.save()
        resource.data_tasks.add(result_task)
    except Exception:
        # TODO: log this exception
        pass


@task_success.connect(sender=get_resource_from_url)
def get_resource_from_url_success(sender, result, **kwargs):
    if sender.request.is_eager:
        result_task = TaskResult.objects.get_task(sender.request.id)
        result_task.result = json.dumps(result)
        result_task.status = 'SUCCESS'
        result_task.save()


@task_failure.connect(sender=get_resource_from_url)
def get_resource_from_url_failure(sender, task_id, exception, args, traceback, einfo, signal, **kwargs):
    resource_id = int(args[0])
    resource = Resource.objects.get(pk=resource_id)
    result = {
        'exc_type': exception.__class__.__name__,
        'exc_message': str(exception),
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type
    }

    result_task = TaskResult.objects.get_task(task_id)
    if sender.request.is_eager:
        result_task.status = 'FAILURE'
    result_task.result = json.dumps(result)
    result_task.save()


@task_success.connect(sender=process_resource_file)
def save_result_on_verify_resource_file_task_success(sender, result, *args, **kwargs):
    if sender.request.is_eager:
        result_task = TaskResult.objects.get_task(sender.request.id)
        result_task.result = json.dumps(result)
        result_task.status = 'SUCCESS'
        result_task.save()


@task_failure.connect(sender=process_resource_file)
def save_result_on_verify_resource_file_task_failure(sender, task_id, exception, args, traceback, einfo, signal,
                                                     **kwargs):
    resource_id = int(args[0])
    resource = Resource.objects.get(pk=resource_id)
    result = {
        'exc_type': exception.__class__.__name__,
        'exc_message': str(exception),
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type
    }

    result_task = TaskResult.objects.get_task(task_id)
    if sender.request.is_eager:
        result_task.status = 'FAILURE'
    result_task.result = json.dumps(result)
    result_task.save()


@task_success.connect(sender=process_file_data)
def save_result_on_process_file_data_task_success(sender, result, *args, **kwargs):
    if sender.request.is_eager:
        result_task = TaskResult.objects.get_task(sender.request.id)
        result_task.result = json.dumps(result)
        result_task.status = 'SUCCESS'
        result_task.save()


@task_failure.connect(sender=process_file_data)
def save_result_on_process_file_data_task_failure(sender, task_id, exception, args, traceback, einfo, signal,
                                                  **kwargs):
    resource_id = int(args[0])
    resource = Resource.objects.get(pk=resource_id)
    result = {
        'exc_type': exception.__class__.__name__,
        'exc_message': str(exception),
        'uuid': str(resource.uuid),
        'link': resource.link,
        'format': resource.format,
        'type': resource.type,
    }

    result_task = TaskResult.objects.get_task(task_id)
    if sender.request.is_eager:
        result_task.status = 'FAILURE'
    result_task.result = json.dumps(result)
    result_task.save()
