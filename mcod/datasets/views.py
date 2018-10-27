# -*- coding: utf-8 -*-

import falcon
from dal import autocomplete
from django.apps import apps
from elasticsearch_dsl import Q

from mcod.datasets.documents import DatasetsDoc
from mcod.datasets.models import Dataset, STATUS_CHOICES
from mcod.datasets.schemas import DatasetsList, ReportCommentsSchema
from mcod.datasets.serializers import DatasetSerializer, DatasetsMeta, ReportCommentResponseSerializer
from mcod.datasets.tasks import send_dataset_comment
from mcod.following.handlers import RetrieveOneFollowHandler, FollowingSearchHandler
from mcod.lib.handlers import SearchHandler, RetrieveOneHandler, CreateHandler
from mcod.lib.triggers import LoginOptional
from mcod.lib.views import SearchView, RetrieveOneView, CreateView
from mcod.resources.documents import ResourceDoc
from mcod.resources.schemas import ResourcesList
from mcod.resources.serializers import ResourceSerializer, ResourcesMeta


class DatasetsView(SearchView):
    class GET(FollowingSearchHandler):
        meta_serializer = DatasetsMeta()
        request_schema = DatasetsList()
        response_serializer = DatasetSerializer(many=True, include_data=('institution',))
        search_document = DatasetsDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            return qs.filter('match', status='published')


class DatasetView(RetrieveOneView):
    class GET(RetrieveOneFollowHandler):
        database_model = apps.get_model('datasets', 'Dataset')
        response_serializer = DatasetSerializer(many=False, include_data=('institution', 'resources'))
        triggers = [LoginOptional(), ]

        def resource_clean(self, request, id, *args, **kwargs):
            model = self.database_model
            try:
                return model.objects.get(pk=id, status="published")
            except model.DoesNotExist:
                raise falcon.HTTPNotFound


class DatasetResourcesView(SearchView):
    class GET(SearchHandler):
        meta_serializer = ResourcesMeta()
        request_schema = ResourcesList()
        response_serializer = ResourceSerializer(many=True)
        search_document = ResourceDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            if 'id' in kwargs:
                qs = qs.query(
                    "nested", path="dataset",
                    query=Q("term", **{'dataset.id': kwargs['id']})
                ).filter('match', status='published')
            return qs


class DatasetResourceView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('resources', 'Resource')
        response_serializer = ResourceSerializer(many=False, include_data=('dataset',))


class DatasetAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Dataset.objects.none()

        qs = Dataset.objects.filter(status=STATUS_CHOICES[0][0])

        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs


class ReportCommentsView(CreateView):
    class POST(CreateHandler):
        request_schema = ReportCommentsSchema()
        response_serializer = ReportCommentResponseSerializer(many=False)
        database_model = apps.get_model('datasets', 'Dataset')

        def _clean(self, request, *args, **kwargs):
            cleaned = super()._clean(request, *args, **kwargs)
            try:
                cleaned['dataset'] = self.database_model.objects.get(pk=kwargs['id'])
            except self.database_model.DoesNotExist:
                raise falcon.HTTPNotFound
            return cleaned

        def _data(self, request, cleaned, *args, **kwargs):
            send_dataset_comment.delay(cleaned['dataset'].id, cleaned['comment'])
            return {}


from django.http import HttpResponse
import json
import pandas as pd
from mcod.datasets.visualizations import *


def getResource(request, id):
    filename = 'postepowaniawszczete-zabojstwo.csv'

    df = pd.read_csv(filename, encoding='iso-8859-2', delimiter=';')
    summary = analyze_df(df)

    return HttpResponse(json.dumps({
        'columns': summary
    }))


def getChartData(request, id):
    type = request.GET.get('type')
    x = request.GET['x']
    y = request.GET.get('y')
    operation = request.GET.get('operation')
    filter = request.GET.get('filter')

    return HttpResponse(json.dumps({
        'x': ['kategoria pierwsza', 'kategoria druga'],
        'y': [10, 20]
    }
    ))
