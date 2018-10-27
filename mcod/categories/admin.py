from django.contrib import admin

from mcod.categories.form import CategoryForm
from mcod.categories.models import Category
from django.utils.translation import gettext_lazy as _
from mcod.lib.admin_mixins import TrashMixin, HistoryMixin


@admin.register(Category)
class CategoryAdmin(HistoryMixin, admin.ModelAdmin):
    form = CategoryForm
    prepopulated_fields = {"slug": ("title",)}
    exclude = ['status_changed', 'is_removed']
    # fields = ['status', 'title', 'slug']
    actions_on_top = True
    list_display = ['slug', 'obj_history']


class CategoryTrash(Category):
    class Meta:
        proxy = True
        verbose_name = _("Trash")
        verbose_name_plural = _("Trash")


@admin.register(CategoryTrash)
class CategoryTrashAdmin(TrashMixin):
    pass
