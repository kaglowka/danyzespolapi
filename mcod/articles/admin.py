from django.contrib import admin
from django.conf import settings

from mcod.lib.admin_mixins import TrashMixin, HistoryMixin

from mcod.articles.models import Article
from mcod.articles.forms import ArticleForm
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe


@admin.register(Article)
class ArticleAdmin(HistoryMixin, admin.ModelAdmin):
    actions_on_top = True
    autocomplete_fields = ['tags', 'license']
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-general',),
                'fields': (
                    "preview_link",
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
                    'license',
                    'status',
                )
            }
        ),
        (
            _("Tags"),
            {
                'classes': ('suit-tab', 'suit-tab-tags',),
                'fields': (
                    "tags",
                )
            }
        ),

    )
    readonly_fields = ['preview_link']
    suit_form_tabs = (
        ('general', _('General')),
        ('tags', _('Tags'))
    )

    list_display = ["title", "status", "created_by", 'preview_link', 'obj_history']
    search_fields = ["title", "created_by__email"]
    form = ArticleForm

    def get_queryset(self, request):
        qs = Article.objects.all()
        self.request = request
        return qs

    def preview_link(self, obj):
        url = f"{settings.BASE_URL}/article/{obj.id}"
        return mark_safe('<a href="%s" class="btn" target="_blank">%s</a>' % (url, _("Preview")))

    preview_link.allow_tags = True
    preview_link.short_description = _("Preview link")

    def save_model(self, request, obj, form, change):
        if 'slug' in form.cleaned_data:
            if form.cleaned_data['slug'] == "":
                obj.slug = slugify(form.cleaned_data['title'])
        if not obj.id:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    class Media:
        js = ("articles/js/hide_license_buttons.js",)


class ArticleTrash(Article):
    class Meta:
        proxy = True
        verbose_name = _("Trash")
        verbose_name_plural = _("Trash")


@admin.register(ArticleTrash)
class ArticleTrashAdmin(TrashMixin):
    list_display = ['title', 'author']
    search_fields = ['title', 'author']
    fields = [
        'title', 'author', 'datasets', 'notes', 'slug', 'status', 'tags', 'license_id', 'is_removed'
    ]
    readonly_fields = [
        'title', 'author', 'datasets', 'notes', 'slug', 'status', 'tags', 'license_id'
    ]
