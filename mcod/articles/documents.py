from django.apps import apps
from django_elasticsearch_dsl import DocType, Index, fields

from mcod.users.models import UserFollowingArticle

from mcod import settings
from mcod.datasets.documents import datasets_field
from mcod.lib.search.analyzers import polish_analyzer, standard_analyzer

Article = apps.get_model('articles', 'Article')
Dataset = apps.get_model('datasets', 'Dataset')
Tag = apps.get_model('tags', 'Tag')

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['articles'])
INDEX.settings(**settings.ELASTICSEARCH_DEFAULT_INDEX_SETTINGS)


@INDEX.doc_type
class ArticleDoc(DocType):
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
            'raw': fields.TextField(),
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

    datasets = datasets_field(attr='published_datasets')
    license = fields.NestedField(
        properties={
            'id': fields.IntegerField(),
            'name': fields.TextField(),
            'title': fields.TextField(),
            'url': fields.TextField()
        }
    )

    tags = fields.KeywordField(attr='tags_list', multi=True)
    views_count = fields.IntegerField()
    users_following = fields.KeywordField(attr='users_following_list', multi=True)
    status = fields.TextField()
    modified = fields.DateField()
    created = fields.DateField()

    class Meta:
        doc_type = 'article'
        model = Article
        related_models = [Tag, Dataset, UserFollowingArticle]

    def get_instances_from_related(self, related_instance):
        if isinstance(related_instance, UserFollowingArticle):
            return related_instance.follower.followed_applications.all()
        if isinstance(related_instance, Dataset):
            return related_instance.articles.all()
        if isinstance(related_instance, Tag):
            return related_instance.articles.all()

    def get_queryset(self):
        return self._doc_type.model.objects.filter(status__in=['published', 'draft'])
