from django import forms
from ckeditor.widgets import CKEditorWidget
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.utils.translation import gettext_lazy as _
from mcod.organizations.models import Organization
from localflavor.pl.forms import PLPostalCodeField, PLREGONField
from mcod.users.models import User


class OrganizationForm(forms.ModelForm):
    description = forms.CharField(
        widget=CKEditorWidget(
            attrs={
                'placeholder': _("Some information about the institution"),
            }
        ),
        label=_("Description"),
        required=False

    )

    slug = forms.SlugField(required=False)

    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(
            verbose_name=_('Users'),
            is_stacked=False
        ),
        label=_("Users")

    )
    postal_code = PLPostalCodeField(label=_("Postal code"))
    regon = PLREGONField()
    website = forms.URLField(label=_("Website"))
    # institution_type = forms.ChoiceField(choices=(
    #     ('local', _('Local goverment')),
    #     ('state', _('Public goverment')),
    #     ('other', _('Other'))),
    #     initial='state',
    #     label=_("Institution type"))

    email = forms.EmailField()

    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['users'].initial = self.instance.users.all()

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        obj = Organization.raw.filter(slug=slug)
        if obj and 'slug' in self.changed_data:
            raise forms.ValidationError(_("That value is already taken"))
        return slug

    def save(self, commit=True):
        super(OrganizationForm, self).save(commit=False)
        if commit:
            self.instance.save()
        if self.instance.pk:
            self.instance.users.set(self.cleaned_data['users'])
            self.save_m2m()
        return self.instance

    class Meta:
        model = Organization
        fields = [
            'slug',
            'title',
            'institution_type',
            'postal_code',
            'city',
            'street',
            'street_number',
            'flat_number',
            'street_type',
            'email',
            'fax',
            'tel',
            'epuap',
            'regon',
            'website',
            'users'
        ]
