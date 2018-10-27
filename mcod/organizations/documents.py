from django.apps import apps
from django_elasticsearch_dsl import DocType, Index, fields

from mcod import settings
from mcod.datasets.documents import datasets_field
from mcod.lib.search.analyzers import polish_analyzer, standard_analyzer

Organization = apps.get_model('organizations', 'Organization')
Dataset = apps.get_model('datasets', 'Dataset')

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['institutions'])
INDEX.settings(**settings.ELASTICSEARCH_DEFAULT_INDEX_SETTINGS)


@INDEX.doc_type
class InstitutionDoc(DocType):
    id = fields.IntegerField()
    slug = fields.TextField()
    title = fields.TextField(
        analyzer=polish_analyzer,
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField()
        }
    )
    description = fields.TextField(
        analyzer=polish_analyzer,
        fields={
            'raw': fields.KeywordField(),
        }
    )
    image_url = fields.TextField(
        attr='image_url'
    )

    postal_code = fields.KeywordField()
    city = fields.TextField(
        analyzer=standard_analyzer,
        fields={
            'raw': fields.KeywordField()
        }, fielddata=True)
    street_type = fields.KeywordField()
    street = fields.TextField(
        analyzer=standard_analyzer,
        fields={
            'raw': fields.KeywordField()
        })
    street_number = fields.KeywordField()
    flat_number = fields.KeywordField()
    email = fields.KeywordField()
    epuap = fields.KeywordField()
    institution_type = fields.KeywordField()
    regon = fields.KeywordField()
    tel = fields.KeywordField()
    tel = fields.KeywordField()
    website = fields.KeywordField()
    datasets = datasets_field(attr='published_datasets')
    status = fields.TextField()
    modified = fields.DateField()
    created = fields.DateField()

    class Meta:
        doc_type = 'institution'
        model = Organization
        related_models = [Dataset]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Dataset):
            return related_instance.organization

    def get_queryset(self):
        return self._doc_type.model.objects.filter(status='published')
