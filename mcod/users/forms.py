from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from mcod.lib.widgets import JsonPairUserInputs
from django.contrib.postgres.forms.jsonb import JSONField
from django.utils.translation import gettext_lazy as _
from mcod.users.models import User
from django.contrib.auth import forms as auth_forms
from mcod.organizations.models import Organization


class UserCreationForm(forms.ModelForm):
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"), widget=forms.PasswordInput,
                                help_text=_("Enter the same password as above, for verification."))
    customfields = JSONField(label=_("Extra info"), required=False,
                             widget=JsonPairUserInputs(val_attrs={'size': 35},
                                                       key_attrs={'class': 'large'}))

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=FilteredSelectMultiple('organizations', False),
        label=_("Organizations")
    )

    class Meta:
        model = User
        fields = ['email', 'customfields', 'fullname', 'is_staff', 'is_superuser', 'state',
                  'organizations']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        super(UserCreationForm, self).save(commit=False)
        self.instance.set_password(self.cleaned_data["password1"])
        if commit:
            self.instance.save()
        if self.instance.pk:
            self.instance.organizations.set(self.cleaned_data['organizations'])
        return self.instance


class UserChangeForm(forms.ModelForm):
    password = auth_forms.ReadOnlyPasswordHashField(label=_("Password"),
                                                    help_text=_(
                                                        "Raw passwords are not stored, so there is no way to see "
                                                        "this user's password, but you can change the password "
                                                        "using <a href=\"../password/\">this form</a>."))

    customfields = JSONField(label=_("Extra info"), required=False,
                             widget=JsonPairUserInputs(val_attrs={'size': 35},
                                                       key_attrs={'class': 'large'}))

    organizations = forms.ModelMultipleChoiceField(
        queryset=Organization.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(_('institutions'), False),
        label=_("Institution")

    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')
        if self.instance.pk:
            self.fields['organizations'].initial = self.instance.organizations.all()

    def clean_password(self):
        return self.initial["password"]

    def save(self, commit=True):
        super(UserChangeForm, self).save(commit=False)
        if commit:
            self.instance.save()
        if self.instance.pk:
            self.instance.organizations.set(self.cleaned_data['organizations'])
        return self.instance
