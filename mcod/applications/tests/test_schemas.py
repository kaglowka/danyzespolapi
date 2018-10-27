from mcod.applications.schemas import ApplicationsList
from mcod.lib.tests.helpers.elasticsearch import QuerysetTestHelper


class TestApplicationsList(object):
    class ApplicationsListTestSchema(QuerysetTestHelper, ApplicationsList):
        pass

    def test_empty_context(self, es_dsl_queryset):
        schema = self.ApplicationsListTestSchema()
        qs = schema.prepare_queryset(es_dsl_queryset, {}).to_dict()
        assert qs == {"query": {"match_all": {}}}

    def test_full_context(self, es_dsl_queryset):
        schema = self.ApplicationsListTestSchema()

        context = {
            'id': {
                'term': 'Blabla',
                'gte': '5',
                'gt': '4',
                'lte': '40',
                'lt': '41',
                'in': ['10', '50', '100']
            },
            'ids': ['46|3|1', '2'],
            'q': ['one', 'notes|two', 'three'],
            'tags': {
                'term': 'zxcv',
                'terms': ['dfg', 'asd'],
                'wildcard': '*abc*',
                'prefix': 'sth',
                'exclude': 'not_wanted'
            },
            'author': {
                'term': 'noone',
                'wildcard': '*one*',
                'prefix': 'dr.',
                'in': ['Tolkien', 'Orwell'],
                'exclude': 'Coelho'
            },
            'facet': ['tags', 'modified'],
            'sort': 'title',
            'highlight': ['notes'],
        }

        qs = schema.prepare_queryset(es_dsl_queryset, context).to_dict()

        assert 'query' in qs
        assert set(qs.keys()) == {'query', 'aggs', 'highlight', 'sort'}

        assert 'bool' in qs['query']
        query_bool = qs['query']['bool']
        sections = ('must', 'filter', 'should', 'must_not')
        assert set(query_bool.keys()) == (set(sections) | {'minimum_should_match'})

        assert all(type(query_bool[key]) == list for key in sections)

        musts = query_bool['must']
        assert len(musts) == 11
        assert {'term': {'author': 'noone'}} in musts
        assert {'wildcard': {'author': '*one*'}} in musts
        assert {'prefix': {'author': 'dr.'}} in musts
        assert {'term': {'tags': 'zxcv'}} in musts
        assert {'wildcard': {'tags': '*abc*'}} in musts
        assert {'prefix': {'tags': 'sth'}} in musts
        assert {'term': {'id': 'Blabla'}} in musts

        for el in musts:
            if 'terms' in el:
                if 'author' in el['terms']:
                    assert set(el['terms']['author']) == {'Tolkien', 'Orwell'}
                if 'tags' in el['terms']:
                    assert set(el['terms']['tags']) == {'dfg', 'asd'}
                if 'id' in el['terms']:
                    assert set(el['terms']['id']) == {'10', '50', '100'}
            if 'ids' in el:
                assert set(el['ids']['values']) == {'46', '3', '1', '2'}

        must_nots = query_bool['must_not']
        assert len(must_nots) == 2
        assert {'term': {'author': 'Coelho'}} in must_nots
        assert {'term': {'tags': 'not_wanted'}} in must_nots

        filters = query_bool['filter']
        assert len(filters) == 4
        assert {'range': {'id': {'gte': '5'}}} in filters
        assert {'range': {'id': {'lte': '40'}}} in filters
        assert {'range': {'id': {'gt': '4'}}} in filters
        assert {'range': {'id': {'lt': '41'}}} in filters

        shoulds = query_bool['should']
        assert len(shoulds) == 11
        assert {'match': {'title': {'query': 'one'}}} in shoulds
        assert {'match': {'title': {'query': 'three'}}} in shoulds
        assert {'match': {'notes': {'query': 'one'}}} in shoulds
        assert {'match': {'notes': {'query': 'two'}}} in shoulds
        assert {'match': {'notes': {'query': 'three'}}} in shoulds
        assert {'match': {'author': {'query': 'one'}}} in shoulds
        assert {'match': {'author': {'query': 'three'}}} in shoulds
        assert {'match': {'tags': {'query': 'one'}}} in shoulds
        assert {'match': {'tags': {'query': 'three'}}} in shoulds
        assert {'match': {'datasets.title': {'query': 'one'}}} in shoulds
        assert {'match': {'datasets.title': {'query': 'three'}}} in shoulds

        aggs = qs['aggs']
        assert set(aggs.keys()) == {'_filter_modified', '_filter_tags'}
        assert 'aggs' in aggs['_filter_modified']
        assert 'modified' in aggs['_filter_modified']['aggs']
        assert 'date_histogram' in aggs['_filter_modified']['aggs']['modified']
        assert aggs['_filter_modified']['aggs']['modified']['date_histogram'] == {
            'field': 'modified',
            'interval': 'month',
            'size': 500,
            'min_doc_count': 0
        }

        assert 'aggs' in aggs['_filter_tags']
        assert 'tags' in aggs['_filter_tags']['aggs']
        assert 'terms' in aggs['_filter_tags']['aggs']['tags']
        assert 'field' in aggs['_filter_tags']['aggs']['tags']['terms']
        assert aggs['_filter_tags']['aggs']['tags']['terms']['field'] == 'tags'

        assert qs['sort'] == ['title.raw']
        assert qs['highlight'] == {
            'fields': {
                'notes': {
                    'post_tags': ['</em>'],
                    'pre_tags': ['<em>']
                }
            }
        }
