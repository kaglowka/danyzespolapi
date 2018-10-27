from django.forms import ModelForm
from django.forms.widgets import TextInput
from mcod.categories.models import Category


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'})
        }
