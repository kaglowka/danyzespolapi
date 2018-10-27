# -*- coding: utf-8 -*-
import falcon
import json
from elasticsearch import TransportError, RequestError
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from elasticsearch_dsl import Search
from elasticsearch_dsl.connections import get_connection

from mcod.lib.handlers import BaseHandler
from mcod.lib.search.facets import NestedFacet
from mcod.lib.views import RetrieveView
from mcod.tools.schemas import StatsSchema
from mcod.tools.serializers import StatsMeta, StatsSerializer

indicies = [
    "articles",
    "applications",
    "institutions",
    "datasets",
    "resources",
]

connection = get_connection()


class StatsView(RetrieveView):
    class GET(BaseHandler):
        request_schema = StatsSchema()
        response_serializer = StatsSerializer(many=False)
        meta_serializer = StatsMeta()

        def _data(self, request, cleaned, *args, explain=None, **kwargs):
            search = Search(using=connection, index=indicies, extra={'size': 0})
            search.aggs.bucket('documents_by_type',
                               TermsFacet(field='_type').get_aggregation()) \
                .bucket('by_month',
                        DateHistogramFacet(field='created', interval='month', min_doc_count=0).get_aggregation())
            search.aggs.bucket('datasets_by_institution',
                               NestedFacet('institution',
                                           TermsFacet(field='institution.id')).get_aggregation())

            search.aggs.bucket('datasets_by_category',
                               NestedFacet('category',
                                           TermsFacet(field='category.id', min_doc_count=1, size=50)).get_aggregation())
            search.aggs.bucket('datasets_by_tags', TermsFacet(field='tags').get_aggregation())
            search.aggs.bucket('datasets_by_formats', TermsFacet(field='formats').get_aggregation())
            search.aggs.bucket('datasets_by_openness_scores', TermsFacet(field='openness_scores').get_aggregation())
            if explain == '1':
                return search.to_dict()
            try:
                return search.execute()
            except TransportError as err:
                raise falcon.HTTPBadRequest(description=err.info['error']['reason'])


class ClusterHealthView(object):
    def on_get(self, request, response, *args, **kwargs):
        response.body = json.dumps(connection.cluster.health())
        response.status = falcon.HTTP_200


class ClusterStateView(object):
    def on_get(self, request, response, *args, **kwargs):
        response.body = json.dumps(connection.cluster.state())
        response.status = falcon.HTTP_200


class ClusterAllocationView(object):
    def on_get(self, request, response, *args, **kwargs):
        try:
            result = connection.cluster.allocation_explain()
        except RequestError:
            result = {}
        response.body = json.dumps(result)
        response.status = falcon.HTTP_200
