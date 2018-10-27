from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from model_utils import Choices
from model_utils.models import StatusModel, TimeStampedModel
from mcod.lib.model_mixins import IndexableMixin
from mcod.lib import storages
from mcod.lib.model_utils import SoftDeletableModel
from mcod.lib.managers import DeletedManager, SoftDeletableManager

User = get_user_model()
INSTITUTION_TYPE_CHOICES = (('local', _('Local goverment')),
                            ('state', _('Public goverment')),
                            ('other', _('Other')),)

STATUS_CHOICES = [
    ('published', _('Published')),
    ('draft', _('Draft')),
]


class Organization(IndexableMixin, StatusModel, SoftDeletableModel, TimeStampedModel):
    STATUS = Choices(*STATUS_CHOICES)
    slug = models.CharField(max_length=254, unique=True, verbose_name=_('Name'))
    title = models.CharField(max_length=100, verbose_name=_('Title'))
    description = models.TextField(blank=True, null=True, verbose_name=_('Description'))
    image = models.ImageField(max_length=254, storage=storages.get_storage('organizations'),
                              upload_to='%Y%m%d',
                              blank=True, null=True, verbose_name=_('Image URL'))
    postal_code = models.CharField(max_length=6, null=True, verbose_name=_('Postal code'))
    city = models.CharField(max_length=200, null=True, verbose_name=_("City"))
    street_type = models.CharField(max_length=50, null=True, verbose_name=_("Street type"))
    street = models.CharField(max_length=200, null=True, verbose_name=_("Street"))
    street_number = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Street number"))
    flat_number = models.CharField(max_length=200, null=True, blank=True, verbose_name=_("Flat number"))

    email = models.CharField(max_length=300, null=True, verbose_name=_("Email"))
    epuap = models.CharField(max_length=500, null=True, verbose_name=_("EPUAP"))
    fax = models.CharField(max_length=50, null=True, verbose_name=_("Fax"))

    institution_type = models.CharField(
        max_length=50,
        choices=INSTITUTION_TYPE_CHOICES,
        default=INSTITUTION_TYPE_CHOICES[1][0],
        verbose_name=_("Institution type"))
    regon = models.CharField(max_length=20, null=True, verbose_name=_("REGON"))
    tel = models.CharField(max_length=50, null=True, verbose_name=_("Phone"))
    website = models.CharField(max_length=200, null=True, verbose_name=_("Website"))

    created_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Created by"),
        related_name='organizations_created'
    )
    modified_by = models.ForeignKey(
        User,
        models.DO_NOTHING,
        blank=False,
        editable=False,
        null=True,
        verbose_name=_("Modified by"),
        related_name='organizations_modified'
    )

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    def __str__(self):
        if self.title:
            return self.title
        return self.slug

    def get_url_path(self):
        if self.id:
            try:
                return reverse("admin:applications_application_change", kwargs={"object_id": self.id})
            except NoReverseMatch:
                return ""
        return ""

    @property
    def image_url(self):
        try:
            return self.image.url
        except ValueError:
            return ''

    @property
    def short_description(self):
        clean_text = ""
        if self.description:
            clean_text = ''.join(BeautifulSoup(self.description, "html.parser").stripped_strings)
        return clean_text

    @property
    def api_url(self):
        return '/institutions/{}'.format(self.id)

    @property
    def description_html(self):
        return format_html(self.description)

    short_description.fget.short_description = _("Description")

    raw = models.Manager()
    objects = SoftDeletableManager()
    deleted = DeletedManager()

    class Meta:
        db_table = "organization"
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")
        default_manager_name = "objects"

    @classmethod
    def accusative_case(cls):
        return _("acc: Institution")

    @property
    def published_datasets(self):
        return self.datasets.filter(status='published')
