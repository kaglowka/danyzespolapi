from mcod.searchhistories.documents import SearchHistoriesDoc
from mcod.searchhistories.schemas import SearchHistoriesList
from mcod.searchhistories.serializers import SearchHistorySerializer
from mcod.lib.handlers import SearchHandler, RetrieveOneHandler
from mcod.lib.serializers import SearchMeta
from django.apps import apps
from mcod.lib.views import SearchView, RetrieveOneView


class SearchHistoriesView(SearchView):
    class GET(SearchHandler):
        meta_serializer = SearchMeta()
        request_schema = SearchHistoriesList()
        response_serializer = SearchHistorySerializer(many=True)
        search_document = SearchHistoriesDoc()


class SearchHistoryView(RetrieveOneView):
    class GET(RetrieveOneHandler):
        database_model = apps.get_model('searchhistories', 'SearchHistory')
        response_serializer = SearchHistorySerializer(many=False)
