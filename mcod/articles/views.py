# -*- coding: utf-8 -*-
import falcon
from django.apps import apps
from elasticsearch_dsl import Q

from mcod.articles.documents import ArticleDoc
from mcod.articles.schemas import ArticlesList
from mcod.articles.serializers import ArticlesSerializer, ArticlesMeta
from mcod.datasets.documents import DatasetsDoc
from mcod.datasets.schemas import DatasetsList
from mcod.datasets.serializers import DatasetSerializer, DatasetsMeta
from mcod.following.handlers import RetrieveOneFollowHandler, FollowingSearchHandler
from mcod.lib.handlers import SearchHandler
from mcod.lib.triggers import LoginOptional
from mcod.lib.views import SearchView, RetrieveOneView


class ArticlesView(SearchView):
    class GET(FollowingSearchHandler):
        meta_serializer = ArticlesMeta()
        request_schema = ArticlesList()
        response_serializer = ArticlesSerializer(many=True)
        search_document = ArticleDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            return qs.filter('match', status='published')


class ArticleView(RetrieveOneView):
    class GET(RetrieveOneFollowHandler):
        database_model = apps.get_model('articles', 'Article')
        response_serializer = ArticlesSerializer(many=False)
        triggers = [LoginOptional(), ]

        def resource_clean(self, request, id, *args, **kwargs):
            model = self.database_model
            user = getattr(request, 'user')
            try:
                if user.is_superuser:
                    return model.objects.get(pk=id, status__in=["published", 'draft'])
                return model.objects.get(pk=id, status="published")
            except model.DoesNotExist:
                raise falcon.HTTPNotFound


class ArticleDatasetsView(SearchView):
    class GET(SearchHandler):
        meta_serializer = DatasetsMeta()
        request_schema = DatasetsList()
        response_serializer = DatasetSerializer(many=True, include_data=('institution',))
        search_document = DatasetsDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            if 'id' in kwargs:
                qs = qs.query("nested", path="articles",
                              query=Q("term", **{'articles.id': kwargs['id']}))
            return qs
