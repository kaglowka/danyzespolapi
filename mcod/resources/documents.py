from django.apps import apps
from django_elasticsearch_dsl import DocType, Index, fields

from mcod import settings
from mcod.lib.search.analyzers import polish_analyzer

Resource = apps.get_model('resources', 'Resource')
Dataset = apps.get_model('datasets', 'Dataset')
TaskResult = apps.get_model('django_celery_results', "TaskResult")

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['resources'])
INDEX.settings(**settings.ELASTICSEARCH_DEFAULT_INDEX_SETTINGS)

data_schema = fields.NestedField(attr='schema', properties={
    'fields': fields.NestedField(properties={
        'name': fields.KeywordField(attr='name'),
        'type': fields.KeywordField(attr='type'),
        'format': fields.KeywordField(attr='format')
    }),
    'missingValue': fields.KeywordField(attr='missingValue')
})

data_field = fields.ObjectField(
    properties={
        'schema': data_schema,
        'headers': fields.KeywordField(attr='tags_list', multi=True)
    }
)


@INDEX.doc_type
class ResourceDoc(DocType):
    id = fields.IntegerField()
    uuid = fields.TextField()
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
    file_url = fields.TextField(
        attr='file_url'
    )
    link = fields.TextField()
    format = fields.TextField()
    type = fields.TextField()
    openness_score = fields.IntegerField()

    dataset = fields.NestedField(properties={
        'id': fields.IntegerField(),
        'title': fields.TextField(
            analyzer=polish_analyzer,
            fields={
                'raw': fields.KeywordField()
            }
        )
    })

    # data = data_field
    views_count = fields.IntegerField()
    downloads_count = fields.IntegerField()

    status = fields.TextField()
    modified = fields.DateField()
    created = fields.DateField()

    class Meta:
        doc_type = 'resource'
        model = Resource
        related_models = [Dataset, ]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, Dataset):
            return related_instance.resources.all()

    def get_queryset(self):
        return self._doc_type.model.objects.filter(status='published')
