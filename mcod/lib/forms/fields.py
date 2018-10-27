# -*- coding: utf-8 -*-
import json

import six
from django import forms
from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.safestring import mark_safe

from mcod.lib.forms.widgets import FormFieldWidget


class JSONField(models.TextField):
    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs',
                                      {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        super(JSONField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value

    def get_db_prep_value(self, value, *args, **kwargs):
        if isinstance(value, six.string_types):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class FormField(forms.MultiValueField):
    def __init__(self, form_class, **kwargs):
        self.form = form_class()
        kwargs['widget'] = FormFieldWidget([f for f in self.form])
        kwargs['initial'] = [f.field.initial for f in self.form]
        kwargs['required'] = False

        self.max_length = kwargs.pop('max_length', None)

        fields = [f.field for f in self.form]

        super(FormField, self).__init__(fields, **kwargs)

    def compress(self, data_list):
        data = {}
        if data_list:
            return dict(
                (f.name, data_list[i]) for i, f in enumerate(self.form))
        return data

    def clean(self, value):
        if not value:
            raise ValidationError(
                'Error found in Form Field: Nothing to validate')

        data = dict((bf.name, value[i]) for i, bf in enumerate(self.form))
        self.form = form = self.form.__class__(data)
        if not form.is_valid():
            error_dict = list(form.errors.items())
            raise ValidationError([
                ValidationError(mark_safe('{} {}'.format(
                    k.title(), v)), code=k) for k, v in error_dict])
        return super(FormField, self).clean(value)


class ModelFormField(JSONField):
    def __init__(self, *args, **kwargs):
        self.form = kwargs.pop('form', None)
        kwargs['null'] = True
        kwargs['blank'] = True
        super(ModelFormField, self).__init__(*args, **kwargs)

    def formfield(self, form_class=FormField, **kwargs):
        return super(ModelFormField, self).formfield(form_class=form_class,
                                                     form=self.form, **kwargs)


class AnyChoiceField(forms.MultipleChoiceField):
    def to_python(self, value):
        if not value:
            return []
        elif not isinstance(value, (list, tuple)):
            value = list(value)
        return [str(val) for val in value]
