from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel, SoftDeletableModel, TimeStampedModel

User = get_user_model()

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Tag(StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    name = models.CharField(unique=True, max_length=100, verbose_name=_("name"))

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='tags_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='tags_modified'

    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        db_table = 'tag'

    def __str__(self):
        return self.name

    @classmethod
    def accusative_case(cls):
        return _("acc: Tag")
