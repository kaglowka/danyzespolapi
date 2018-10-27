from django.contrib import admin
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mcod.applications.forms import ApplicationForm
from mcod.applications.models import Application
from mcod.lib.admin_mixins import TrashMixin, HistoryMixin


@admin.register(Application)
class ApplicationAdmin(HistoryMixin, admin.ModelAdmin):
    actions_on_top = True
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ['tags']
    readonly_fields = ['application_logo']
    fieldsets = (
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-general',),
                'fields': (
                    "title",
                )
            }
        ),

        (
            'url',
            {
                'classes': ('collapse', 'suit-tab', 'suit-tab-general',),
                'fields': (
                    "slug",
                )
            }
        ),

        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-general',),
                'fields': (
                    "notes",
                    'author',
                    "url",
                    "image",
                    'application_logo',
                    "status",
                )
            }
        ),
        (
            _("Datasets"),
            {
                'classes': ('suit-tab', 'suit-tab-datasets',),
                'fields': (
                    "datasets",
                )
            }
        ),
        (
            'Tags',
            {
                'classes': ('suit-tab', 'suit-tab-tags',),
                'fields': (
                    "tags",
                )
            }
        )
    )

    list_display = ["title", "created_by", 'application_logo', 'modified', "status", 'obj_history']
    search_fields = ["title", "created_by__email", "url"]
    list_filter = ["status"]
    list_editable = ["status"]

    suit_form_tabs = (
        ('general', _('General')),
        ('tags', _('Tags')),
        ('datasets', _('Datasets'))
    )

    form = ApplicationForm

    def application_logo(self, obj):
        try:
            product_url = reverse(
                "admin:%s_%s_change" % (obj._meta.app_label, obj._meta.model_name),
                args=(obj.id,)
            )
        except NoReverseMatch:
            product_url = ''

        html = ''
        if obj.image:
            html = mark_safe('<a href="%s" target="_blank"><img src="%s" alt="" width="150" /></a>' % (
                product_url,
                obj.image.url
            ))

        return html

    application_logo.short_description = _("Logo")

    def save_model(self, request, obj, form, change):
        if 'slug' in form.cleaned_data:
            if form.cleaned_data['slug'] == "":
                obj.slug = slugify(form.cleaned_data['title'])
        if not obj.id:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    def get_queryset(self, request):
        qs = Application.objects.all()
        return qs


class Trash(Application):
    class Meta:
        proxy = True
        verbose_name = _("Trash")
        verbose_name_plural = _("Trash")


@admin.register(Trash)
class TrashApplicationAdmin(TrashMixin):
    list_display = ['title', 'author', 'url']
    search_fields = ['title', 'author', 'url']
    fields = [
        'title', 'author', 'datasets', 'image', 'notes', 'slug', 'status', 'tags', 'url', 'is_removed'
    ]
    readonly_fields = [
        'title', 'author', 'datasets', 'image', 'notes', 'slug', 'status', 'tags', 'url',
    ]
