# -*- coding: utf-8 -*-
import falcon
from django.apps import apps

from mcod.counters.lib import Counter
from mcod.lib.handlers import SearchHandler, RetrieveOneHandler, UpdateHandler
from mcod.lib.views import SearchView, RetrieveOneView, UpdateView
from mcod.resources.documents import ResourceDoc
from mcod.resources.schemas import ResourcesList
from mcod.resources.serializers import ResourceSerializer, ResourcesMeta, ResourceDataSerializer


class ResourcesView(SearchView):
    class GET(SearchHandler):
        meta_serializer = ResourcesMeta()
        request_schema = ResourcesList()
        response_serializer = ResourceSerializer(many=True)
        search_document = ResourceDoc()


class ResourceView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('resources', 'Resource')
        response_serializer = ResourceSerializer(many=False, include_data=('dataset',))

        def _clean(self, request, id, *args, **kwargs):
            model = self.database_model
            try:
                return model.objects.get(pk=id, status="published")
            except model.DoesNotExist:
                raise falcon.HTTPNotFound


class ResourceDataView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('resources', 'Resource')
        response_serializer = ResourceDataSerializer(many=False)

        def _clean(self, request, id, *args, **kwargs):
            model = self.database_model
            try:
                return model.objects.get(pk=id, status="published")
            except model.DoesNotExist:
                raise falcon.HTTPNotFound

        def _data(self, request, cleaned, *args, **kwargs):
            if cleaned.data_is_valid == 'SUCCESS':
                try:
                    schema, headers, data = cleaned.data.data
                    return {
                        'id': cleaned.id,
                        'schema': schema,
                        'headers': headers,
                        'data': data
                    }

                except Exception:
                    return {}


class ResourceDownloadCounter(UpdateView):
    class PUT(UpdateHandler):
        response_serializer = ResourceDataSerializer(many=False)

        def _clean(self, request, **kwargs):
            return {'resource_id': kwargs['id']}

        def _data(self, request, cleaned, *args, **kwargs):
            counter = Counter()
            counter.incr_download_count(cleaned['resource_id'])
            return None
