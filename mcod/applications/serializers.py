import marshmallow as ma

from mcod.lib.fields import Relationship, TagsList
from mcod.lib.serializers import BasicSerializer, ArgsListToDict, SearchMeta, BucketItem
from mcod.datasets.serializers import DatasetSchema


class Aggregations(ArgsListToDict):
    by_modified = ma.fields.Nested(BucketItem(), many=True, attribute='_filter_modified.modified.buckets')
    by_tag = ma.fields.Nested(BucketItem(), many=True, attribute='_filter_tags.tags.buckets')


class ApplicationsMeta(SearchMeta):
    aggs = ma.fields.Nested(Aggregations, attribute='aggregations')


class ApplicationsSerializer(BasicSerializer):
    id = ma.fields.Int(dump_only=True, faker_type='integer')
    slug = ma.fields.Str(faker_type='slug')
    title = ma.fields.Str(faker_type='sentence')
    notes = ma.fields.Str(faker_type='sentence')
    author = ma.fields.Str(faker_type='firstname')
    url = ma.fields.Str(faker_type='url')
    image_url = ma.fields.Str(faker_type='image_url')
    datasets = Relationship(
        related_url='/applications/{app_id}/datasets',
        related_url_kwargs={'app_id': '<id>'},
        many=True,
        type_='dataset',
        faker_count=10,
        faker_schema=DatasetSchema
    )
    followed = ma.fields.Boolean(faker_type='boolean')
    tags = TagsList(ma.fields.String, faker_type='tagslist')
    views_count = ma.fields.Integer(faker_type='integer')
    modified = ma.fields.Str(faker_type='datetime')
    created = ma.fields.Str(faker_type='datetime')

    class Meta:
        type_ = "applications"
        self_url_many = "/applications"
        self_url = '/applications/{app_id}'
        self_url_kwargs = {"app_id": "<id>"}
