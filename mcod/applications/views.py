# -*- coding: utf-8 -*-

from django.apps import apps
from elasticsearch_dsl.query import Q

from mcod.applications.documents import ApplicationsDoc
from mcod.applications.schemas import ApplicationsList, ApplicationProposal
from mcod.applications.serializers import ApplicationsSerializer, ApplicationsMeta
from mcod.applications.tasks import send_application_proposal
from mcod.datasets.documents import DatasetsDoc
from mcod.datasets.schemas import DatasetsList
from mcod.datasets.serializers import DatasetSerializer, DatasetsMeta
# from mcod.histories.schemas import HistoryList
from mcod.following.handlers import FollowingSearchHandler
from mcod.histories.serializers import HistorySerializer
from mcod.lib.handlers import (
    SearchHandler,
    RetrieveHistoryHandler,
    CreateHandler)
from mcod.following.handlers import RetrieveOneFollowHandler
from mcod.lib.triggers import LoginOptional
from mcod.lib.views import SearchView, RetrieveOneView, CreateView


class ApplicationsView(SearchView):
    doc_template = 'applications_view.apibp'

    class GET(FollowingSearchHandler):
        meta_serializer = ApplicationsMeta()
        request_schema = ApplicationsList()
        response_serializer = ApplicationsSerializer(many=True)
        search_document = ApplicationsDoc()


class ApplicationView(RetrieveOneView):
    class GET(RetrieveOneFollowHandler):
        database_model = apps.get_model('applications', 'Application')
        response_serializer = ApplicationsSerializer(many=False)
        triggers = [LoginOptional(), ]


class ApplicationHistoryView(SearchView):
    class GET(RetrieveHistoryHandler):
        table_name = 'application'
        response_serializer = HistorySerializer(many=True)


class ApplicationDatasetsView(SearchView):
    class GET(SearchHandler):
        meta_serializer = DatasetsMeta()
        request_schema = DatasetsList()
        response_serializer = DatasetSerializer(many=True, include_data=('institution',))
        search_document = DatasetsDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            if 'id' in kwargs:
                qs = qs.query("nested", path="applications",
                              query=Q("term", **{'applications.id': kwargs['id']}))
            return qs


class ApplicationProposalForm(CreateView):
    class POST(CreateHandler):
        databse_model = apps.get_model('applications', 'Application')
        request_schema = ApplicationProposal()

        def _data(self, request, cleaned, *args, **kwargs):
            send_application_proposal.delay(cleaned)

        def _serialize(self, data, meta, links=None, *args, **kwargs):
            return {}


__doc_views__ = [
    ApplicationsView,
    ApplicationView,
    ApplicationDatasetsView,
    ApplicationHistoryView,
    ApplicationProposalForm
]
