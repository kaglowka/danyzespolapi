import marshmallow as ma
import marshmallow_jsonapi as ja

from mcod.datasets.models import FREQUENCY
from mcod.lib.fields import Relationship, TagsList
from mcod.lib.serializers import BasicSerializer, ArgsListToDict, SearchMeta, BucketItem
from mcod.resources.serializers import ResourceSchema
from django.utils.translation import gettext as _

UPDATE_FREQUENCY = dict(FREQUENCY)


class Aggregations(ArgsListToDict):
    by_institution = ma.fields.Nested(BucketItem(app='organizations', model='Organization'),
                                      attribute='_filter_institutions.institutions.inner.buckets', many=True)
    by_category = ma.fields.Nested(BucketItem(app='categories', model='Category'),
                                   attribute='_filter_categories.categories.inner.buckets', many=True)
    by_format = ma.fields.Nested(BucketItem(), attribute='_filter_formats.formats.buckets', many=True)
    by_tag = ma.fields.Nested(BucketItem(), attribute='_filter_tags.tags.buckets', many=True)
    by_openness_scores = ma.fields.Nested(BucketItem(), attribute='_filter_openness_scores.openness_scores.buckets',
                                          many=True)


class DatasetsMeta(SearchMeta):
    aggs = ma.fields.Nested(Aggregations, attribute='aggregations')


class DatasetInstitution(ja.Schema):
    id = ma.fields.Int()
    title = ma.fields.Str()

    class Meta:
        type_ = 'institution'
        strict = True
        self_url = '/institutions/{institution_id}'
        self_url_kwargs = {"institution_id": "<id>"}


class DatasetCategory(ma.Schema):
    id = ma.fields.Int()
    title = ma.fields.Dict()


class DatasetSchema(ja.Schema):
    id = ma.fields.Int(dump_only=True, faker_type='integer')
    title = ma.fields.Str(faker_type='sentence')
    notes = ma.fields.Str(faker_type='sentence')
    formats = ma.fields.List(ma.fields.Str(), attr='formats')
    category = ma.fields.Nested(DatasetCategory, many=False)
    downloads_count = ma.fields.Integer()
    tags = TagsList(ma.fields.Str())
    openness_scores = ma.fields.List(ma.fields.Int())
    license_condition_db_or_copyrighted = ma.fields.String()
    license_condition_modification = ma.fields.Boolean()
    license_condition_original = ma.fields.Boolean()
    license_condition_responsibilities = ma.fields.String()
    license_condition_source = ma.fields.Boolean()
    license_condition_timestamp = ma.fields.Boolean()
    license_name = ma.fields.String()
    license_description = ma.fields.String()
    update_frequency = ma.fields.Method('update_frequency_translated')
    views_count = ma.fields.Integer()
    url = ma.fields.String()
    modified = ma.fields.Method('last_modified_resource_date')  # TODO: powinny być dwa pola o różnych wartościach
    # last_modified_resource = ma.fields.Str()
    created = ma.fields.Str()

    def last_modified_resource_date(self, obj):
        return str(obj.last_modified_resource)

    def update_frequency_translated(self, obj):
        if obj.update_frequency and obj.update_frequency in UPDATE_FREQUENCY:
            return _(UPDATE_FREQUENCY[obj.update_frequency])
        return None

    class Meta:
        type_ = 'dataset'
        strict = True
        self_url_many = "/datasets"
        self_url = '/datasets/{dataset_id}'
        self_url_kwargs = {"dataset_id": "<id>"}


class DatasetSerializer(DatasetSchema, BasicSerializer):
    institution = Relationship(
        related_url='/institutions/{institution_id}',
        related_url_kwargs={'institution_id': '<institution.id>'},
        schema=DatasetInstitution,
        many=False,
        type_='institution'
    )
    resources = Relationship(
        related_url='/datasets/{dataset_id}/resources',
        related_url_kwargs={'dataset_id': '<id>'},
        schema=ResourceSchema,
        many=True,
        type_='resource'
    )
    followed = ma.fields.Boolean()

    class Meta:
        type_ = 'dataset'
        strict = True
        self_url_many = "/datasets"
        self_url = '/datasets/{dataset_id}'
        self_url_kwargs = {"dataset_id": "<id>"}


class ReportCommentResponseSerializer(ja.Schema):
    id = ma.fields.Int(dump_only=True)

    class Meta:
        type_ = 'reportcomment'
