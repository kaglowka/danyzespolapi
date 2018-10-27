import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel

from mcod.following.models import UsersFollowingMixin
from mcod.lib.managers import DeletedManager, SoftDeletableManager
from mcod.lib.model_mixins import CounterMixin, IndexableMixin
from mcod.lib.model_utils import TimeStampedModel, SoftDeletableModel

User = get_user_model()

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Article(CounterMixin, IndexableMixin, UsersFollowingMixin, StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4)
    slug = models.SlugField(unique=True, max_length=100, verbose_name=_("Slug"))
    title = models.CharField(max_length=300, verbose_name=_("Title"))
    notes = RichTextUploadingField(verbose_name=_("Notes"), null=True)
    license_old_id = models.CharField(max_length=20, blank=True, null=True, verbose_name=_("License ID"))
    license = models.ForeignKey('licenses.License', on_delete=models.DO_NOTHING, blank=True, null=True,
                                verbose_name=_("License ID"))
    author = models.CharField(max_length=50,
                              blank=True,
                              null=True,
                              verbose_name=_("Author"))
    tags = models.ManyToManyField('tags.Tag',
                                  db_table='article_tag',
                                  blank=True,
                                  verbose_name=_("Tags"),
                                  related_name='articles',
                                  related_query_name="article")
    datasets = models.ManyToManyField('datasets.Dataset',
                                      db_table='article_dataset',
                                      verbose_name=_('Datasets'),
                                      related_name='articles',
                                      related_query_name="article")

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='articles_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='articles_modified'
    )

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    @property
    def tags_list(self):
        return [tag.name for tag in self.tags.all()]

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        db_table = "article"
        default_manager_name = "objects"

    @classmethod
    def accusative_case(cls):
        return _("acc: Article")

    def __str__(self):
        return self.title

    def published_datasets(self):
        return self.datasets.filter(status='published')
