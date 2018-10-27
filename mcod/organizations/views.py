# -*- coding: utf-8 -*-
import falcon
from dal import autocomplete
from django.apps import apps
from elasticsearch_dsl import Q

from mcod.datasets.documents import DatasetsDoc
from mcod.datasets.schemas import DatasetsList
from mcod.datasets.serializers import DatasetSerializer, DatasetsMeta
from mcod.lib.handlers import SearchHandler, RetrieveOneHandler
from mcod.lib.triggers import LoginOptional
from mcod.lib.views import SearchView, RetrieveOneView
from mcod.organizations.documents import InstitutionDoc
from mcod.organizations.models import Organization
from mcod.organizations.schemas import InstitutionsList
from mcod.organizations.serializers import InstitutionsSerializer, InstitutionsMeta


class InstitutionsView(SearchView):
    class GET(SearchHandler):
        meta_serializer = InstitutionsMeta()
        request_schema = InstitutionsList()
        response_serializer = InstitutionsSerializer(many=True)
        search_document = InstitutionDoc()


class InstitutionView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('organizations', 'Organization')
        response_serializer = InstitutionsSerializer(many=False, include_data=('datasets',))
        triggers = [LoginOptional(), ]

        def resource_clean(self, request, id, *args, **kwargs):
            model = self.database_model
            try:
                return model.objects.get(pk=id, status="published")
            except model.DoesNotExist:
                raise falcon.HTTPNotFound


class InstitutionDatasetsView(SearchView):
    class GET(SearchHandler):
        meta_serializer = DatasetsMeta()
        request_schema = DatasetsList()
        response_serializer = DatasetSerializer(many=True)
        search_document = DatasetsDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            if 'id' in kwargs:
                qs = qs.query("nested", path="institution",
                              query=Q("term", **{'institution.id': kwargs['id']}))
            return qs


class OrganizationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Organization.objects.none()

        qs = Organization.objects.all()

        if self.q:
            qs = qs.filter(title__icontains=self.q)

        return qs
