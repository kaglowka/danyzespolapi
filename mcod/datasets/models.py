import uuid

from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Max
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel

from mcod.following.models import UsersFollowingMixin
from mcod.lib.managers import DeletedManager, SoftDeletableManager
from mcod.lib.model_mixins import CounterMixin, IndexableMixin
from mcod.lib.model_utils import TimeStampedModel, SoftDeletableModel, skip_signal

User = get_user_model()

FREQUENCY = (
    ("notApplicable", _("Not applicable")),
    ("yearly", _("yearly")),
    ("everyHalfYear", _("every half year")),
    ("quarterly", _("quarterly")),
    ("monthly", _("monthly")),
    ("weekly", _("weekly")),
    ("daily", _("daily")),
)

TYPE = (
    ('application', _('application')),
    ('dataset', _('dataset')),
    ('article', _('article'))
)

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Dataset(CounterMixin, IndexableMixin, UsersFollowingMixin, StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4)
    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=300, null=True, verbose_name=_("Title"))
    version = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Version"))
    url = models.CharField(max_length=1000, blank=True, null=True, verbose_name=_("Url"))
    notes = models.TextField(verbose_name=_("Notes"), null=True)

    license_old_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("License ID"))
    license = models.ForeignKey('licenses.License', on_delete=models.DO_NOTHING, blank=True, null=True,
                                verbose_name=_("License ID"))

    license_condition_db_or_copyrighted = models.CharField(max_length=300, blank=True, null=True)
    license_condition_modification = models.NullBooleanField(null=True, blank=True, default=None)
    license_condition_original = models.NullBooleanField(null=True, blank=True, default=None)
    license_condition_responsibilities = models.TextField(blank=True, null=True)
    license_condition_source = models.NullBooleanField(null=True, blank=True, default=None)
    license_condition_timestamp = models.NullBooleanField(null=True, blank=True)
    organization = models.ForeignKey('organizations.Organization', on_delete=models.CASCADE, related_name='datasets',
                                     verbose_name=_('Institution'))
    customfields = JSONField(blank=True, null=True, verbose_name=_("Customfields"))
    update_frequency = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Update frequency"))
    category = models.ForeignKey('categories.Category', models.DO_NOTHING, blank=True, null=True,
                                 verbose_name=_('Category'))
    tags = models.ManyToManyField('tags.Tag',
                                  db_table='dataset_tag',
                                  blank=True,
                                  verbose_name=_("Tag"),
                                  related_name='datasets',
                                  related_query_name="dataset")

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='datasets_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='datasets_modified'

    )
    skip_signal = False
    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    class Meta:
        verbose_name = _("Dataset")
        verbose_name_plural = _("Datasets")
        db_table = 'dataset'
        default_manager_name = "objects"

    def __str__(self):
        return self.title

    @property
    def institution(self):
        return self.organization

    @property
    def downloads_count(self):
        return sum(res.downloads_count for res in self.resources.all())

    @property
    def formats(self):
        return list(set(res.format for res in self.resources.all() if res.format is not None))

    @property
    def openness_scores(self):
        return list(set(res.openness_score for res in self.resources.all()))

    @property
    def tags_list(self):
        # TODO: implement this
        return [tag.name for tag in self.tags.all()]

    @property
    def license_name(self):
        return self.license.name if self.license and self.license.name else ''

    @property
    def license_description(self):
        return self.license.title if self.license and self.license.title else ''

    @property
    def last_modified_resource(self):
            return self.resources.all().aggregate(Max('modified'))['modified__max']

    last_modified_resource.fget.short_description = _("modified")

    @classmethod
    def accusative_case(cls):
        return _("acc: Dataset")


@receiver(post_save, sender=Dataset)
@skip_signal()
def dataset_post_save(sender, instance, **kwargs):
    if instance.is_removed is True:
        for resource in instance.resources.all():
            resource.is_removed = True
            resource.save()


@receiver(pre_save, sender=Dataset)
@skip_signal()
def dataset_pre_save(sender, instance, **kwargs):
    instance.slug = get_unique_slug(instance.id, instance.title, sender.raw)


def get_unique_slug(id, slug, model_manager):
    slug = slugify(slug)
    unique_slug = slug
    counter = 1
    while model_manager.filter(slug=unique_slug).exists():
        # slug - powinien być unique w bazie danych
        # sprawdzamy czy instancja jest edytowana
        # TODO: sprawdźić czy slug jest indeksowany w bazie
        if (model_manager.filter(slug=unique_slug).values('id')[0]['id'] == id):
            break
        unique_slug = '{}-{}'.format(slug, counter)
        counter += 1
    return unique_slug
