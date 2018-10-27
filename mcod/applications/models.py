import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel

from mcod.following.models import UsersFollowingMixin
from mcod.lib.model_utils import TimeStampedModel, SoftDeletableModel
from mcod.lib import storages
from mcod.lib.managers import DeletedManager, SoftDeletableManager
from mcod.lib.model_mixins import CounterMixin, IndexableMixin

User = get_user_model()

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Application(CounterMixin, IndexableMixin, UsersFollowingMixin, StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4)
    slug = models.SlugField(unique=True, max_length=100, verbose_name=_("Slug"))
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    notes = models.TextField(verbose_name=_("Notes"), null=True)
    author = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Author"))
    url = models.URLField(max_length=300, verbose_name=_("App URL"), null=True)
    image = models.ImageField(
        max_length=200, storage=storages.get_storage('applications'),
        upload_to='%Y%m%d', blank=True, null=True, verbose_name=_("Image URL")
    )
    datasets = models.ManyToManyField('datasets.Dataset',
                                      db_table='application_dataset',
                                      verbose_name=_('Datasets'),
                                      related_name='applications',
                                      related_query_name="application")
    tags = models.ManyToManyField('tags.Tag',
                                  blank=True,
                                  db_table='application_tag',
                                  verbose_name=_('Tag'),
                                  related_name='applications',
                                  related_query_name="application")

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='applications_created'
    )

    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='applications_modified'
    )

    @property
    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            return ''

    @property
    def tags_list(self):
        return [tag.name for tag in self.tags.all()]

    @property
    def users_following_list(self):
        return [user.id for user in self.users_following.all()]

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    def __str__(self):
        return self.title

    @classmethod
    def accusative_case(cls):
        return _("acc: Application")

    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")
        db_table = "application"
        default_manager_name = "objects"

    def published_datasets(self):
        return self.datasets.filter(status='published')
