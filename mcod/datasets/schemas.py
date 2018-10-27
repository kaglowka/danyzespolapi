# coding: utf-8
from elasticsearch_dsl import TermsFacet
from marshmallow import Schema

from mcod.lib import fields
from mcod.lib.schemas import List
from mcod.lib.search import constants
from mcod.lib.search.facets import NestedFacet
from mcod.lib.error_messages import str_error_messages


class DatasetsList(List):
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

    notes = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_FILTER_REGEXP,
        constants.LOOKUP_QUERY_CONTAINS,
        constants.LOOKUP_QUERY_ENDSWITH,
        constants.LOOKUP_QUERY_STARTSWITH
    ])

    category = fields.NestedFilteringField('category', field_name='category.id', lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_GT,
        constants.LOOKUP_QUERY_GTE,
        constants.LOOKUP_QUERY_LT,
        constants.LOOKUP_QUERY_LTE,
        constants.LOOKUP_QUERY_IN
    ])

    institution = fields.NestedFilteringField('institution', field_name='institution.id', lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_GT,
        constants.LOOKUP_QUERY_GTE,
        constants.LOOKUP_QUERY_LT,
        constants.LOOKUP_QUERY_LTE,
        constants.LOOKUP_QUERY_IN
    ])

    tags = fields.FilteringFilterField(
        lookups=[
            constants.LOOKUP_FILTER_TERM,
            constants.LOOKUP_FILTER_TERMS,
            constants.LOOKUP_FILTER_WILDCARD,
            constants.LOOKUP_FILTER_PREFIX,
            constants.LOOKUP_QUERY_IN,
            constants.LOOKUP_QUERY_EXCLUDE
        ]
    )

    formats = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_QUERY_IN
    ])

    openness_scores = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_FILTER_WILDCARD,
        constants.LOOKUP_FILTER_PREFIX,
        constants.LOOKUP_QUERY_IN,
        constants.LOOKUP_QUERY_EXCLUDE
    ])

    q = fields.SearchFilterField(
        search_fields=['title', 'notes'],
    )

    facet = fields.FacetedFilterField(
        facets={
            'institutions': NestedFacet('institution', TermsFacet(field='institution.id', size=500)),
            'categories': NestedFacet('category', TermsFacet(field='category.id', size=500)),
            'tags': TermsFacet(field='tags', size=500),
            'formats': TermsFacet(field='formats', size=500),
            'openness_scores': TermsFacet(field='openness_scores')
        },
    )

    sort = fields.OrderingFilterField(
        ordering_fields={
            "id": "id",
            "title": "title.raw",
            "modified": "last_modified_resource",
            "created": "created"
        }
    )

    class Meta:
        strict = True


class ReportCommentsSchema(Schema):
    comment = fields.Str(required=True, error_messages=str_error_messages,
                         faker_type='comment', example='Looks unpretty')

    class Meta:
        strict = True
