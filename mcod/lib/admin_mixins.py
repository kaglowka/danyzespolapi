from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from django.urls import reverse, NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import gettext_lazy as _


class TrashMixin(admin.ModelAdmin):

    def get_queryset(self, request):
        return self.model.deleted.all()

    def has_add_permission(self, request, obj=None):
        return False


class HistoryMixin(object):

    def history_view(self, request, object_id, extra_context=None):
        """The 'history' admin view for this model."""
        from mcod.histories.models import History as LogEntry
        # First check if the user can see this history.
        model = self.model
        obj = self.get_object(request, unquote(object_id))
        if obj is None:
            return self._get_obj_does_not_exist_redirect(request, model._meta, object_id)

        if not self.has_change_permission(request, obj):
            raise PermissionDenied

        # Then get the history for this object.
        opts = model._meta
        app_label = opts.app_label
        action_list = LogEntry.objects.exclude(
            change_user_id=1
        ).filter(
            table_name=opts.db_table,
            row_id=obj.id
        ).order_by('-change_timestamp')
        action_list = (x for x in action_list if x.difference != "{}")
        context = dict(
            self.admin_site.each_context(request),
            title=_('Change history: %s') % obj,
            action_list=action_list,
            module_name=str(capfirst(opts.verbose_name_plural)),
            object=obj,
            opts=opts,
            preserved_filters=self.get_preserved_filters(request),
        )
        context.update(extra_context or {})

        request.current_app = self.admin_site.name

        return TemplateResponse(request, self.object_history_template or [
            "admin/%s/%s/object_history.html" % (app_label, opts.model_name),
            "admin/%s/object_history.html" % app_label,
            "admin/object_history.html"
        ], context)

    def obj_history(self, obj):
        try:
            product_url = reverse(
                "admin:%s_%s_history" % (obj._meta.app_label, obj._meta.model_name),
                args=(obj.id,)
            )
        except NoReverseMatch:
            product_url = ''

        html = mark_safe('<a href="%s" target="_blank">%s</a>' % (
            product_url,
            _("History")
        ))

        return html

    obj_history.short_description = _('History')
