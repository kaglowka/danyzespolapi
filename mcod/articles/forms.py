from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.utils.translation import gettext_lazy as _

from mcod.articles.models import Article


class ArticleForm(forms.ModelForm):
    title = forms.CharField(required=True, label=_("Title"),
                            widget=forms.Textarea(attrs={'style': 'width: 99%', 'rows': 1}))
    notes = forms.CharField(widget=CKEditorUploadingWidget, required=True, label=_("Notes"))
    slug = forms.CharField(required=False)

    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'notes', 'author', 'license', 'status', 'tags'
        ]
