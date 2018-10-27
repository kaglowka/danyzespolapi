import marshmallow as ma
import marshmallow_jsonapi as ja
from django.apps import apps


class BucketItem(ma.Schema):
    key = ma.fields.Raw()
    title = ma.fields.String()
    doc_count = ma.fields.Integer()

    def __init__(self, app=None, model=None, extra=None, only=(), exclude=(), prefix='', strict=None,
                 many=False, context=None, load_only=(), dump_only=(),
                 partial=False):

        self.model = apps.get_model(app, model) if app and model else None
        super().__init__(extra=extra, only=only, exclude=exclude, prefix=prefix, strict=strict, many=many,
                         context=context, load_only=load_only, dump_only=dump_only, partial=partial)

    @ma.pre_dump(pass_many=True)
    def update_item(self, data, many):
        _valid_model = self.model and hasattr(self.model, 'title')
        if _valid_model:
            objects = self.model.raw.filter(pk__in=[item['key'] for item in data])
        ret = []
        for item in data:
            if _valid_model:
                try:
                    obj = objects.get(pk=item['key'])
                    item['title'] = obj.title
                    ret.append(item)
                except self.model.DoesNotExist:
                    pass
            else:
                item['title'] = item['key']
                ret.append(item)

        return ret


class BasicSerializer(ja.Schema):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.links = {}

    def dump(self, data, meta, links=None, many=None, update_fields=True, **kwargs):
        self.included_data = {}
        self.document_meta, self.links = meta, links or {}
        return super().dump(data, many=many, update_fields=update_fields, **kwargs)

    def wrap_response(self, data, many):
        return {
            'data': data,
            'links': self.links
        }


class ArgsListToDict(ma.Schema):
    @ma.pre_dump
    def prepare_data(self, obj):
        return obj.to_dict()


class SearchMeta(ma.Schema):
    count = ma.fields.Integer(missing=0, attribute='hits.total')
    took = ma.fields.Integer(missing=0, attribute='took')
    max_score = ma.fields.Float(attribute='hits.max_score')
#

# class Suggestions(ma.Schema):
#     @ma.pre_dump
#     def prepare_suggestions(self, obj):
#         data = {}
#         for field in self.fields:
#             if field in obj['suggest']:
#                 data = obj['suggest'].to_dict()[field][0]
#                 data['options'] = [item['_source'] for item in data['options']]
#         return data
