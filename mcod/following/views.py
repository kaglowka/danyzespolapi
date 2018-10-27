from django.apps import apps
from mcod.datasets.documents import DatasetsDoc

from mcod.applications.documents import ApplicationsDoc
from mcod.applications.schemas import ApplicationsList
from mcod.applications.serializers import ApplicationsSerializer, ApplicationsMeta
from mcod.articles.documents import ArticleDoc
from mcod.articles.schemas import ArticlesList
from mcod.articles.serializers import ArticlesSerializer, ArticlesMeta
from mcod.datasets.schemas import DatasetsList
from mcod.datasets.serializers import DatasetSerializer, DatasetsMeta
from mcod.following.handlers import CreateFollowingHandler, DeleteFollowingHandler, FollowedListHandler
from mcod.lib.views import (
    CreateView,
    RemoveView,
    SearchView
)


class FollowApplication(CreateView, RemoveView):
    class POST(CreateFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingApplication')
        resource_model = apps.get_model('applications', 'Application')
        resource_name = 'application'
        response_serializer = ApplicationsSerializer(many=False)

    class DELETE(DeleteFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingApplication')
        resource_model = apps.get_model('applications', 'Application')
        resource_name = 'application'
        response_serializer = ApplicationsSerializer(many=False)


class FollowDataset(CreateView, RemoveView):
    class POST(CreateFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingDataset')
        resource_model = apps.get_model('datasets', 'Dataset')
        resource_name = 'dataset'
        response_serializer = DatasetSerializer(many=False)

    class DELETE(DeleteFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingDataset')
        resource_model = apps.get_model('datasets', 'Dataset')
        resource_name = 'dataset'
        response_serializer = DatasetSerializer(many=False)


class FollowArticle(CreateView, RemoveView):
    class POST(CreateFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingArticle')
        resource_model = apps.get_model('articles', 'Article')
        resource_name = 'article'
        response_serializer = ArticlesSerializer(many=False)

    class DELETE(DeleteFollowingHandler):
        database_model = apps.get_model('users', 'UserFollowingArticle')
        resource_model = apps.get_model('articles', 'Article')
        resource_name = 'article'
        response_serializer = ArticlesSerializer(many=False)


class ListOfFollowedApplications(SearchView):
    class GET(FollowedListHandler):
        meta_serializer = ApplicationsMeta()
        request_schema = ApplicationsList()
        response_serializer = ApplicationsSerializer(many=True)
        search_document = ApplicationsDoc()


class ListOfFollowedArticles(SearchView):
    class GET(FollowedListHandler):
        meta_serializer = ArticlesMeta()
        request_schema = ArticlesList()
        response_serializer = ArticlesSerializer(many=True)
        search_document = ArticleDoc()


class ListOfFollowedDatasets(SearchView):
    class GET(FollowedListHandler):
        meta_serializer = DatasetsMeta()
        request_schema = DatasetsList()
        response_serializer = DatasetSerializer(many=True, include_data=('institution',))
        search_document = DatasetsDoc()
