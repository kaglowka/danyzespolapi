from django.apps import apps
from django_elasticsearch_dsl import DocType, Index, fields

from mcod import settings
from mcod.datasets.documents import datasets_field
from mcod.lib.search.analyzers import polish_analyzer, standard_analyzer
from mcod.users.models import UserFollowingApplication

Application = apps.get_model('applications', 'Application')
Dataset = apps.get_model('datasets', 'Dataset')
Tag = apps.get_model('tags', 'Tag')

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['applications'])
INDEX.settings(**settings.ELASTICSEARCH_DEFAULT_INDEX_SETTINGS)


@INDEX.doc_type
class ApplicationsDoc(DocType):
    id = fields.IntegerField()
    slug = fields.KeywordField()
    title = fields.TextField(
        analyzer=polish_analyzer,
        fields={
            'raw': fields.KeywordField(),
            'suggest': fields.CompletionField()
        }
    )
    notes = fields.TextField(
        analyzer=polish_analyzer,
        fields={
            'raw': fields.KeywordField(),
        }
    )

    author = fields.TextField(
        analyzer=standard_analyzer,
        fields={
            'raw': fields.KeywordField(),
            # TODO: fix author data before this
            # 'suggest': fields.CompletionField()
        }
    )

    url = fields.KeywordField()

    image_url = fields.KeywordField(
        attr='image_url'
    )

    datasets = datasets_field(attr='published_datasets')
    users_following = fields.KeywordField(attr='users_following_list', multi=True)

    tags = fields.KeywordField(attr='tags_list', multi=True)

    views_count = fields.IntegerField()
    status = fields.KeywordField()
    modified = fields.DateField()
    created = fields.DateField()

    class Meta:
        doc_type = 'application'
        model = Application
        related_models = [Tag, Dataset, UserFollowingApplication]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, UserFollowingApplication):
            return related_instance.follower.followed_applications.all()
        if isinstance(related_instance, Dataset):
            return related_instance.applications.all()
        if isinstance(related_instance, Tag):
            return related_instance.applications.all()

    def get_queryset(self):
        return self._doc_type.model.objects.filter(status='published')
