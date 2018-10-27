from mcod.histories.documents import HistoriesDoc
from mcod.histories.schemas import HistoriesList
from mcod.histories.serializers import HistorySerializer
from mcod.lib.handlers import SearchHandler, RetrieveOneHandler
from mcod.lib.serializers import SearchMeta
from django.apps import apps
from mcod.lib.views import SearchView, RetrieveOneView


class HistoriesView(SearchView):
    class GET(SearchHandler):
        meta_serializer = SearchMeta()
        request_schema = HistoriesList()
        response_serializer = HistorySerializer(many=True)
        search_document = HistoriesDoc()

        def _queryset(self, cleaned, *args, **kwargs):
            qs = super()._queryset(cleaned, *args, **kwargs)
            return qs.exclude('terms', change_user_id=[1])


class HistoryView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('histories', 'History')
        response_serializer = HistorySerializer(many=False)
