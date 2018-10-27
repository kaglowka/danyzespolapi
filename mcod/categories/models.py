from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.managers import SoftDeletableManager
from model_utils.models import StatusModel, SoftDeletableModel, TimeStampedModel
from mcod.lib import storages
from mcod.lib.managers import DeletedManager

User = get_user_model()

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Category(StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    slug = models.SlugField(max_length=100, unique=True)
    # TODO: change to VarChar(100)
    title = models.TextField(verbose_name=_("Title"))
    description = models.TextField(null=True, verbose_name=_("Description"))
    color = models.CharField(max_length=20, default="#000000", null=True, verbose_name=_("Color"))
    image = models.ImageField(
        max_length=200, storage=storages.get_storage('common'),
        upload_to='', blank=True, null=True, verbose_name=_("Image URL")
    )
    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='categories_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='categories_modified'

    )

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    class Meta:
        db_table = "category"
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
        default_manager_name = "objects"

    @classmethod
    def accusative_case(cls):
        return _("acc: Category")

    def __str__(self):
        return self.slug
