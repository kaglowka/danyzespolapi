# coding: utf-8
from elasticsearch_dsl import TermsFacet

from mcod.lib import fields
from mcod.lib.schemas import List
from mcod.lib.search import constants


class ResourcesList(List):
    id = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_GT,
        constants.LOOKUP_QUERY_GTE,
        constants.LOOKUP_QUERY_LT,
        constants.LOOKUP_QUERY_LTE,
        constants.LOOKUP_QUERY_IN
    ])
    ids = fields.IdsSearchField()

    title = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_FILTER_REGEXP,
        constants.LOOKUP_QUERY_CONTAINS,
        constants.LOOKUP_QUERY_ENDSWITH,
        constants.LOOKUP_QUERY_STARTSWITH
    ])

    description = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_FILTER_REGEXP,
        constants.LOOKUP_QUERY_CONTAINS,
        constants.LOOKUP_QUERY_ENDSWITH,
        constants.LOOKUP_QUERY_STARTSWITH
    ])

    dataset = fields.NestedFilteringField('dataset', field_name='dataset.id', lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_GT,
        constants.LOOKUP_QUERY_GTE,
        constants.LOOKUP_QUERY_LT,
        constants.LOOKUP_QUERY_LTE,
        constants.LOOKUP_QUERY_IN
    ])

    formats = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_IN
    ])

    type = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_IN
    ])

    openness_score = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_GT,
        constants.LOOKUP_QUERY_GTE,
        constants.LOOKUP_QUERY_LT,
        constants.LOOKUP_QUERY_LTE,
        constants.LOOKUP_QUERY_IN
    ])

    q = fields.SearchFilterField(
        search_fields=['title', 'description'],
    )

    facet = fields.FacetedFilterField(
        facets={
            'formats': TermsFacet(field='formats', size=500),
            'types': TermsFacet(fields='type', size=500),
            'openness_score': TermsFacet(field='openness_score', size=500)
        },
    )

    sort = fields.OrderingFilterField(
        ordering_fields={
            "id": "id",
            "title": "title.raw",
            "modified": "modified",
            "created": "created"
        }
    )

    class Meta:
        strict = True
