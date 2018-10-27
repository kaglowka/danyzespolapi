import marshmallow as ma

from mcod.datasets.serializers import DatasetSchema
from mcod.lib.fields import Relationship, TagsList
from mcod.lib.serializers import BasicSerializer, ArgsListToDict, SearchMeta, BucketItem


class Aggregations(ArgsListToDict):
    by_modified = ma.fields.Nested(BucketItem(), many=True, attribute='_filter_modified.modified.buckets')
    by_tag = ma.fields.Nested(BucketItem(), many=True, attribute='_filter_tags.tags.buckets')


class ArticlesMeta(SearchMeta):
    aggs = ma.fields.Nested(Aggregations, attribute='aggregations')


class ArticleLicense(ma.Schema):
    id = ma.fields.Int()
    name = ma.fields.Str()
    title = ma.fields.Str()
    url = ma.fields.Str()
#
# class ArticleDatasetsSerializer(DatasetSerializer):
#     class Meta:
#         type_ = 'datasets'
#         strict = True
#         self_url_many = "/datasets"
#         self_url = '/datasets/{dataset_id}'
#         self_url_kwargs = {"dataset_id": "<id>"}


class ArticlesSerializer(BasicSerializer):
    id = ma.fields.Int(dump_only=True)
    slug = ma.fields.Str()
    title = ma.fields.Str()
    notes = ma.fields.Str()
    author = ma.fields.Str()
    datasets = Relationship(
        related_url='/articles/{article_id}/datasets',
        related_url_kwargs={'article_id': '<id>'},
        schema=DatasetSchema,
        many=True,
        type_='dataset'
    )
    tags = TagsList(ma.fields.String)
    views_count = ma.fields.Integer()
    followed = ma.fields.Boolean()

    modified = ma.fields.Str()
    created = ma.fields.Str()
    license = ma.fields.Nested(ArticleLicense, many=False)

    class Meta:
        type_ = "articles"
        self_url_many = "/articles"
        self_url = '/articles/{article_id}'
        self_url_kwargs = {"article_id": "<id>"}
