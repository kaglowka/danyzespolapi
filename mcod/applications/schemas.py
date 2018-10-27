# coding: utf-8
from elasticsearch_dsl import DateHistogramFacet, TermsFacet
from marshmallow import Schema

from mcod.lib import fields
from mcod.lib.error_messages import str_error_messages
from mcod.lib.schemas import List
from mcod.lib.search import constants


class ApplicationsList(List):
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
    q = fields.SearchFilterField(
        search_fields=['title', 'notes', 'author', 'tags', 'datasets.title'],
    )

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

    author = fields.FilteringFilterField(lookups=[
        constants.LOOKUP_FILTER_TERM,
        constants.LOOKUP_FILTER_TERMS,
        constants.LOOKUP_FILTER_WILDCARD,
        constants.LOOKUP_FILTER_PREFIX,
        constants.LOOKUP_QUERY_IN,
        constants.LOOKUP_QUERY_EXCLUDE
    ])

    facet = fields.FacetedFilterField(
        facets={
            'tags': TermsFacet(field='tags', size=500),
            'modified': DateHistogramFacet(field='modified', interval='month', size=500)
        },
    )

    sort = fields.OrderingFilterField(
        default_ordering=['-modified', ],
        ordering_fields={
            "id": "id",
            "title": "title.raw",
            "modified": "modified",
            "created": "created"
        }
    )

    highlight = fields.HighlightBackend(
        highlight_fields={
            'title': {
                'options': {
                    'pre_tags': ['<em>'],
                    'post_tags': ['</em>'],
                },
                'enabled': True
            },
            'notes': {
                'options': {
                    'pre_tags': ['<em>'],
                    'post_tags': ['</em>'],
                },
                'enabled': True
            }
        }
    )

    class Meta:
        strict = True


class ApplicationProposal(Schema):
    applicant_email = fields.Email(required=True)
    title = fields.Str(required=True, error_messages=str_error_messages,
                       faker_type='application title', example='Some App')
    url = fields.Url(required=True)
    notes = fields.Str(required=True)
    image = fields.Raw(required=False)
    datasets = fields.List(fields.Int(), required=False)

    class Meta:
        strict = True
