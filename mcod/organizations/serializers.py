import marshmallow as ma

from mcod.datasets.serializers import DatasetSchema
from mcod.lib.fields import Relationship
from mcod.lib.serializers import BasicSerializer, ArgsListToDict, SearchMeta, BucketItem


class Aggregations(ArgsListToDict):
    by_city = ma.fields.Nested(BucketItem(), many=True, attribute='_filter_cities.cities.buckets')
    by_type = ma.fields.Nested(BucketItem(), many=True,
                               attribute='_filter_types.types.buckets')


class InstitutionsMeta(SearchMeta):
    aggs = ma.fields.Nested(Aggregations, attribute='aggregations')


class InstitutionsSerializer(BasicSerializer):
    id = ma.fields.Int()
    slug = ma.fields.Str()
    title = ma.fields.Str()
    description = ma.fields.Str()
    image_url = ma.fields.Str()
    postal_code = ma.fields.Str()
    city = ma.fields.Str()
    street_type = ma.fields.Str()
    street = ma.fields.Str()
    street_number = ma.fields.Str()
    flat_number = ma.fields.Str()
    email = ma.fields.Str()
    epuap = ma.fields.Str()
    fax = ma.fields.Str()
    tel = ma.fields.Str()
    regon = ma.fields.Str()
    website = ma.fields.Str()
    institution_type = ma.fields.Str()
    datasets = Relationship(
        related_url='/institutions/{inst_id}/datasets',
        related_url_kwargs={'inst_id': '<id>'},
        schema=DatasetSchema,
        many=True,
        type_='dataset'
    )
    followed = ma.fields.Boolean()
    modified = ma.fields.Str()
    created = ma.fields.Str()

    class Meta:
        type_ = "institutions"
        self_url_many = "/institutions"
        self_url = '/institutions/{inst_id}'
        self_url_kwargs = {"inst_id": "<id>"}
