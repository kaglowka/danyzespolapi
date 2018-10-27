import csv

from dal_admin_filters import AutocompleteFilter
from django.contrib import admin
from django.db.models import Subquery, OuterRef
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_celery_results.models import TaskResult

from mcod.lib.admin_mixins import TrashMixin, HistoryMixin
from mcod.resources.forms import ChangeResourceForm, AddResourceForm
from mcod.resources.models import Resource  # , ResourceView

task_status_to_css_class = {
    'SUCCESS': 'fas fa-check-circle text-success',
    'PENDING': 'fas fa-question-circle text-warning',
    'FAILURE': 'fas fa-times-circle text-error',
    None: 'fas fa-minus-circle text-light'
}


class DatasetFilter(AutocompleteFilter):
    field_name = 'dataset'
    autocomplete_url = 'dataset-autocomplete'
    is_placeholder_title = False
    widget_attrs = {
        'data-placeholder': _('Filter by dataset name')
    }


class TaskStatus(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return (
            ('SUCCESS', 'SUCCESS'),
            ('FAILURE', 'ERROR'),
            ('PENDING', 'WAITING'),
            ('N/A', 'UNAVAILABLE')
        )

    def queryset(self, request, queryset):
        val = self.value()
        if not val:
            return queryset
        val = None if val == 'N/A' else val
        return queryset.filter(**{self.qs_param: val})


class LinkStatusFilter(TaskStatus):
    title = _('Link status')
    parameter_name = 'link_status'
    qs_param = '_link_status'


class FileStatusFilter(TaskStatus):
    title = _('File status')
    parameter_name = 'file_status'
    qs_param = '_file_status'


class TabularViewFilter(TaskStatus):
    title = _('TabularView')
    parameter_name = 'tabular_view_status'
    qs_param = '_data_status'


@admin.register(Resource)
class ResourceAdmin(HistoryMixin, admin.ModelAdmin):
    actions_on_top = True
    change_suit_form_tabs = (
        ('general', _('General')),
        ('file', _('File validation')),
        ('link', _('Link validation')),
        ('data', _('Data validation'))
    )

    add_suit_form_tabs = (
        ('general', _('General')),
    )

    change_fieldsets = [
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-general'),
                'fields': (
                    'link',
                    'file',
                    'title',
                    'description',
                    'format',
                    'dataset',
                    'status',
                    'modified',
                    'created',
                    'type',
                    'file_info',
                    'file_encoding',
                )
            }
        ),
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-file'),
                'fields': (
                    'file_tasks',
                )
            }
        ),
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-link'),
                'fields': (
                    'link_tasks',
                )
            }
        ),
        (
            None,
            {
                'classes': ('suit-tab', 'suit-tab-data'),
                'fields': (
                    'data_tasks',
                )
            }
        ),
    ]

    add_fieldsets = [
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('switcher', 'file', 'link'),
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('title', 'description'),
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('dataset',),
        }),
        (None, {
            'classes': ('suit-tab', 'suit-tab-general'),
            'fields': ('status',),
        }),

    ]

    change_readonly_fields = (
        'format',
        'file',
        'link',
        'modified',
        'created',
        'type',
        'file_info',
        'file_encoding',
        'link_tasks',
        'file_tasks',
        'data_tasks',
    )

    add_readonly_fields = ()

    list_display = [
        'title',
        'uuid',
        'format',
        'dataset',
        'status',
        'type',
        'link_status',
        'file_status',
        'tabular_view',
        'modified'
        # 'obj_history'
    ]

    list_filter = [
        DatasetFilter,
        "format",
        "type",
        "status",
        LinkStatusFilter,
        FileStatusFilter,
        TabularViewFilter
    ]
    search_fields = ['title', 'uuid']
    autocomplete_fields = ['dataset']
    add_form = AddResourceForm
    form = ChangeResourceForm

    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['id', 'title', 'dataset', 'organization', 'link_valid', 'file_valid', 'message']

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response, delimiter=';')

        writer.writerow(field_names)
        for obj in queryset:
            id_ = obj.id
            title = obj.title
            dataset = obj.dataset
            organization = obj.dataset.organization
            link_valid = obj.link_is_valid
            file_valid = obj.file_is_valid

            last_task = obj.link_tasks.last()
            message = ""
            if last_task:
                message = obj.link_tasks.last().result

            row = [id_, title, dataset, organization, link_valid, file_valid, message]
            writer.writerow(row)

        return response

    export_as_csv.short_description = _("Export selected to CSV")

    def get_fieldsets(self, request, obj=None):
        return self.change_fieldsets if obj else self.add_fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj=obj, **defaults)

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = self.change_readonly_fields if obj and obj.id else self.add_readonly_fields
        return readonly_fields

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update(
            {
                'suit_form_tabs': self.change_suit_form_tabs if obj else self.add_suit_form_tabs
            }
        )
        return super().render_change_form(request, context, add=add, change=change, form_url=form_url, obj=obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_staff and not request.user.is_superuser:
            qs = qs.filter(dataset__organization__in=request.user.organizations.iterator())

        link_tasks = TaskResult.objects.filter(link_task_resources=OuterRef('pk')).order_by('-date_done')
        qs = qs.annotate(
            _link_status=Subquery(
                link_tasks.values('status')[:1])
        )
        file_tasks = TaskResult.objects.filter(file_task_resources=OuterRef('pk')).order_by('-date_done')
        qs = qs.annotate(
            _file_status=Subquery(
                file_tasks.values('status')[:1])
        )

        data_tasks = TaskResult.objects.filter(data_task_resources=OuterRef('pk')).order_by('-date_done')
        qs = qs.annotate(
            _data_status=Subquery(
                data_tasks.values('status')[:1])
        )

        return qs

    def get_field_queryset(self, db, db_field, request):
        if 'object_id' in request.resolver_match.kwargs:
            resource_id = int(request.resolver_match.kwargs['object_id'])
            if db_field.name == 'link_tasks':
                return db_field.remote_field.model._default_manager.filter(
                    link_task_resources__id=resource_id,
                )
            if db_field.name == 'file_tasks':
                return db_field.remote_field.model._default_manager.filter(
                    file_task_resources__id=resource_id,
                )
            if db_field.name == 'data_tasks':
                return db_field.remote_field.model._default_manager.filter(
                    data_task_resources__id=resource_id,
                )

        super().get_field_queryset(db, db_field, request)

    def _format_list_status(self, val):
        return format_html('<i class="%s"></i>' % task_status_to_css_class[val])

    def link_status(self, obj):
        return self._format_list_status(obj._link_status)

    link_status.admin_order_field = '_link_status'
    link_status.short_description = format_html('<i class="fas fa-link"></i>')

    def file_status(self, obj):
        return self._format_list_status(obj._file_status)

    file_status.admin_order_field = '_file_status'
    file_status.short_description = format_html('<i class="fas fa-file"></i>')

    def tabular_view(self, obj):
        return self._format_list_status(obj._data_status)

    tabular_view.admin_order_field = '_data_status'
    tabular_view.short_description = format_html('<i class="fas fa-table"></i>')

    def save_model(self, request, obj, form, change):
        if not obj.id:
            obj.created_by = request.user
        obj.modified_by = request.user
        obj.save()

    def get_changeform_initial_data(self, request):
        """
        Get the initial form data from the request's GET params.
        """

        from django.db import models
        from django.core.exceptions import FieldDoesNotExist

        obj_id = request.GET.get('from_id')
        initial = {}
        if obj_id:
            data = model_to_dict(Resource.objects.get(pk=obj_id))
            initial['title'] = data.get('title')
            initial['description'] = data.get('description')
            initial['status'] = data.get('status')
            initial['dataset'] = data.get('dataset')

        for k in initial:
            try:
                f = self.model._meta.get_field(k)
            except FieldDoesNotExist:
                continue
            # We have to special-case M2Ms as a list of comma-separated PKs.
            if isinstance(f, models.ManyToManyField):
                initial[k] = initial[k].split(",")
        return initial

    class Media:
        css = {
            'all': ('./fontawesome/css/all.min.css',)
        }


class Trash(Resource):
    class Meta:
        proxy = True
        verbose_name = _("Trash")
        verbose_name_plural = _("Trash")


@admin.register(Trash)
class TrashAdmin(TrashMixin):
    list_display = ['title', 'dataset', 'modified']
    search_fields = ['title', 'dataset__title']
    fields = [
        'file',
        'link',
        'title',
        'description',
        'dataset',
        'status',
        'is_removed',
    ]

    readonly_fields = [
        'file',
        'link',
        'title',
        'description',
        'dataset',
        'status',
    ]

    def get_queryset(self, request):
        qs = Resource.deleted.all()
        if request.user.is_superuser:
            return qs
        return qs.filter(dataset__organization_id__in=request.user.organizations.all())
