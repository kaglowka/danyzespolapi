from ckeditor.widgets import CKEditorWidget
from django import forms
from django.contrib.postgres.forms.jsonb import JSONField
from django.utils.translation import gettext_lazy as _

from mcod.datasets.models import FREQUENCY, Dataset, get_unique_slug
from mcod.lib.widgets import JsonPairDatasetInputs


class DatasetForm(forms.ModelForm):
    title = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': _('e.g. the name of the data set'),
                   'style': 'width: 99%', 'rows': 1}),
        label=_("Title")
    )
    slug = forms.CharField(label="URL", widget=forms.TextInput(attrs={'size': 85}), required=False)
    notes = forms.CharField(
        widget=CKEditorWidget(
            attrs={
                'placeholder': _("Some information about the data being added"),
                'cols': 80,
                'rows': 10
            }
        ),
        required=False,
        label=_('Notes')
    )
    update_frequency = forms.ChoiceField(
        choices=FREQUENCY,
        label=_("Update frequency")
    )
    url = forms.URLField(required=False,
                         widget=forms.TextInput(
                             attrs={
                                 'size': 85
                             }
                         ),
                         label=_("Source")
                         )

    customfields = JSONField(label=_("Customfields"),
                             widget=JsonPairDatasetInputs(
                                 val_attrs={'size': 35},
                                 key_attrs={'class': 'large'}
                             ),
                             required=False)

    license_condition_source = forms.BooleanField(
        label=_(
            "The recipient should inform about the date, "
            "time of completion and obtaining information from the obliged entity"
        ),
        required=False
    )

    license_condition_modification = forms.BooleanField(
        label=_("The recipient should inform about the processing of the information when it modifies it"),
        required=False
    )

    license_condition_responsibilities = forms.CharField(
        label=_("The scope of the provider's responsibility for the information provided"),
        widget=CKEditorWidget,
        required=False
    )

    license_condition_db_or_copyrighted = forms.CharField(
        label=_("Conditions for using public information that meets the characteristics of the work or constitute "
                "a database (Article 13 paragraph 2 of the Act on the re-use of public sector information)"),
        widget=CKEditorWidget,
        required=False
    )

    class Meta:
        model = Dataset
        fields = [
            'title',
            'slug',
            'category',
            'notes',
            'tags',
            'organization',
            'url',
            'update_frequency',
            'customfields',
            'license_condition_db_or_copyrighted',
            'license_condition_modification',
            'license_condition_responsibilities',
            'license_condition_source',
            'status',
        ]

    def clean_slug(self):
        self.cleaned_data['slug'] = get_unique_slug(self.auto_id, self.data['slug'], Dataset.raw)

    # def full_clean(self):
    #     super().full_clean()


class DatasetListForm(forms.ModelForm):
    title = forms.HiddenInput(attrs={'required': False})
    slug = forms.HiddenInput(attrs={'required': False})


class AddDatasetForm(DatasetForm):
    pass
