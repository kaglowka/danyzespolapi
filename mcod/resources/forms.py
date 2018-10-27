import json

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class ResourceSourceSwitcher(forms.widgets.HiddenInput):
    input_type = 'hidden'
    template_name = 'admin/forms/widgets/resources/switcher.html'


class ResourceSwitcherField(forms.Field):
    def validate(self, value):
        if value not in ('file', 'link'):
            return ValidationError('No option choosed')


class ResourceFileWidget(forms.widgets.FileInput):
    template_name = 'admin/forms/widgets/resources/file.html'


class ResourceLinkWidget(forms.widgets.URLInput):
    template_name = 'admin/forms/widgets/resources/url.html'


class ResourceTasksListField(forms.Field):
    def prepare_value(self, value):
        prepared = []
        for task in value:
            prepared.append(
                {
                    'id': task.task_id,
                    'status': task.status,
                    'date_done': task.date_done,
                    'error': True if task.traceback else False,
                    'traceback': json.loads(task.result) if task.result and task.traceback else None
                }
            )
        return prepared

    def to_python(self, value):
        return value


class ResourceTasksWidget(forms.widgets.Widget):
    template_name = 'admin/forms/widgets/resources/tasks_list.html'

    def get_context(self, name, value, attrs):
        context = {}
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value': value,
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
        }
        return context


class ResourceListForm(forms.ModelForm):
    link = forms.HiddenInput(attrs={'required': False})
    file = forms.HiddenInput(attrs={'required': False})


class ChangeResourceForm(forms.ModelForm):
    link_tasks = ResourceTasksListField(label='URL Validation History', widget=ResourceTasksWidget)
    file_tasks = ResourceTasksListField(label='File Validation History', widget=ResourceTasksWidget)
    data_tasks = ResourceTasksListField(label='Data Validation History', widget=ResourceTasksWidget)
    title = forms.CharField(
        widget=forms.Textarea(
            attrs={'style': 'width: 99%', 'rows': 1}),
        label=_("Title")
    )
    description = forms.CharField(widget=CKEditorWidget, label=_("Description"))


class AddResourceForm(forms.ModelForm):
    switcher = ResourceSwitcherField(label=_('Data source'), widget=ResourceSourceSwitcher)
    file = forms.FileField(label=_('File'), widget=ResourceFileWidget)
    link = forms.URLField(widget=ResourceLinkWidget(attrs={'style': 'width: 99%'}))
    title = forms.CharField(
        widget=forms.Textarea(
            attrs={'style': 'width: 99%', 'rows': 1}),
        label=_("Title")
    )
    description = forms.CharField(widget=CKEditorWidget, label=_("Description"))

    def clean_link(self):
        value = self.cleaned_data.get('link')
        if not value:
            return None
        return value

    def clean_switcher(self):
        switcher_field = self.fields['switcher']
        selected_field = switcher_field.widget.value_from_datadict(self.data, self.files, self.add_prefix('switcher'))
        if selected_field == 'file':
            self.fields['link'].required = False
        elif selected_field == 'link':
            self.fields['file'].required = False

        return selected_field

    class Media:
        js = (
            "https://gitcdn.github.io/bootstrap-toggle/2.2.2/js/bootstrap-toggle.min.js",
        )
        css = {
            'all': [
                "https://gitcdn.github.io/bootstrap-toggle/2.2.2/css/bootstrap-toggle.min.css",
            ]
        }
