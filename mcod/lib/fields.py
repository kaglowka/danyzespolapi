import marshmallow_jsonapi as ja
import operator
import six
from django.db.models.manager import BaseManager
from elasticsearch_dsl.query import Q, Bool
from flatdict import FlatDict
from marshmallow import fields
from marshmallow.exceptions import ValidationError
from marshmallow.utils import missing as missing_
from marshmallow_jsonapi.utils import resolve_params

from mcod.lib.search import constants


class Relationship(ja.fields.Relationship):
    def get_value(self, attr, obj, accessor=None, default=missing_):
        _rel = getattr(obj, attr)
        if isinstance(_rel, BaseManager):
            return _rel.all()

        return super().get_value(attr, obj, accessor=accessor, default=default)

    def get_related_url(self, obj):
        if self.related_url:
            params = resolve_params(obj, self.related_url_kwargs, default=self.default)
            non_null_params = {
                key: value for key, value in params.items()
                if value is not None
            }
            if non_null_params:
                attr = getattr(obj, self.load_from)
                ret = {
                    'href': self.related_url.format(**non_null_params),
                }
                if self.many:
                    count = attr.count() if isinstance(attr, BaseManager) else len(attr)
                    ret['meta'] = {
                        'count': count
                    }

                return ret
        return None


class TagsList(fields.List):
    def serialize(self, attr, obj, accessor=None):
        _rel = getattr(obj, attr)
        if isinstance(_rel, BaseManager):
            return [i.name for i in _rel.all()]

        return super().serialize(attr, obj, accessor=accessor)


class DataMixin:
    def prepare_data(self, name, data):
        return data

    def prepare_queryset(self, queryset, context=None):
        return queryset


class SearchFieldMixin:
    @staticmethod
    def _filter_empty(l):
        return list(filter(lambda el: el != '', l))

    def split_lookup_value(self, value, maxsplit=-1):
        return self._filter_empty(value.split(constants.SEPARATOR_LOOKUP_VALUE, maxsplit))

    def split_lookup_filter(self, value, maxsplit=-1):
        return self._filter_empty(value.split(constants.SEPARATOR_LOOKUP_FILTER, maxsplit))

    def split_lookup_complex_value(self, value, maxsplit=-1):
        return self._filter_empty(value.split(constants.SEPARATOR_LOOKUP_COMPLEX_VALUE, maxsplit))


class Raw(DataMixin, fields.Raw):
    pass


class Nested(DataMixin, fields.Nested):
    pass


class List(DataMixin, fields.List):
    pass


class String(DataMixin, fields.String):
    pass


Str = String


class UUID(DataMixin, fields.UUID):
    pass


class Number(DataMixin, fields.Number):
    pass


class Integer(DataMixin, fields.Integer):
    pass


Int = Integer


class Decimal(DataMixin, fields.Decimal):
    pass


class Boolean(DataMixin, fields.Boolean):
    pass


class FormattedString(DataMixin, fields.FormattedString):
    pass


class Float(DataMixin, fields.Float):
    pass


class DateField(DataMixin, fields.DateTime):
    pass


class Time(DataMixin, fields.Time):
    pass


class Date(DataMixin, fields.Date):
    pass


class TimeDelta(DataMixin, fields.TimeDelta):
    pass


class Dict(DataMixin, fields.Dict):
    pass


class Url(DataMixin, fields.Url):
    pass


class Email(DataMixin, fields.Email):
    pass


class Method(DataMixin, fields.Method):
    pass


class Function(DataMixin, fields.Function):
    pass


class Constant(DataMixin, fields.Constant):
    pass


class FilteringFilterField(SearchFieldMixin, DataMixin, fields.Field):
    def __init__(self, field_name='', lookups=None, **metadata):
        super().__init__(**metadata)
        self.lookups = lookups if isinstance(lookups, list) else []
        self.field_name = field_name

    @property
    def _name(self):
        return self.field_name or self.name

    def prepare_data(self, name, data):
        data = dict(data)
        if name in data:
            nkey = '%s%s%s' % (name, constants.SEPARATOR_LOOKUP_FILTER, constants.LOOKUP_FILTER_TERM)
            data[nkey] = data.pop(name)
        field_data = {k: v for k, v in data.items() if k.startswith(name)}
        data.update(FlatDict(field_data, delimiter=constants.SEPARATOR_LOOKUP_FILTER).as_dict())
        return data

    def _deserialize(self, value, attr, data):
        if isinstance(value, str):
            return {constants.LOOKUP_FILTER_TERM: value}
        return value

    def _validate(self, values):
        unsupported_lookups = list(set(values.keys() - self.lookups))
        if unsupported_lookups:
            raise ValidationError('Unsupported filter')

    def get_range_params(self, value):
        __values = self.split_lookup_value(value, maxsplit=3)
        __len_values = len(__values)

        if __len_values == 0:
            return {}

        params = {
            'gte': __values[0]
        }

        if __len_values == 3:
            params['lte'] = __values[1]
            params['boost'] = __values[2]
        elif __len_values == 2:
            params['lte'] = __values[1]

        return params

    def get_gte_lte_params(self, value, lookup):
        __values = self.split_lookup_value(value, maxsplit=2)
        __len_values = len(__values)

        if __len_values == 0:
            return {}

        params = {
            lookup: __values[0]
        }

        if __len_values == 2:
            params['boost'] = __values[1]

        return params

    def prepare_queryset(self, queryset, context=None):  # noqa:C901
        data = context or self.context
        if not data:
            return queryset
        for lookup, value in data.items():
            func = getattr(self, 'get_filter_{}'.format(lookup), None)
            if not func:
                continue
            q = func(value)
            if q:
                queryset = queryset.query(q)

        return queryset

    def get_filter_term(self, value):
        return Q('term', **{self._name: value})

    def get_filter_terms(self, value):
        if isinstance(value, (list, tuple)):
            __values = value
        else:
            __values = self.split_lookup_value(value)

        return Q(
            'terms',
            **{self._name: __values}
        )

    def get_filter_range(self, value):
        return Q(
            'range',
            **{self._name: self.get_range_params(value)}
        )

    def get_filter_exists(self, value):
        _value_lower = value.lower()
        if _value_lower in constants.TRUE_VALUES:
            return Q("exists", field=self._name)
        elif _value_lower in constants.FALSE_VALUES:
            return ~Q("exists", field=self._name)
        return None

    def get_filter_prefix(self, value):
        return Q(
            'prefix',
            **{self._name: value}
        )

    def get_filter_wildcard(self, value):
        return Q('wildcard', **{self._name: value})

    def get_filter_contains(self, value):
        return Q('wildcard', **{self._name: '*{}*'.format(value)})

    def get_filter_startswith(self, value):
        return Q('prefix', **{self._name: '{}'.format(value)})

    def get_filter_endswith(self, value):
        return Q('wildcard', **{self._name: '*{}'.format(value)})

    def get_filter_in(self, value):
        return self.get_filter_terms(value)

    def get_filter_gt(self, value):
        return Bool(filter=[
            Q('range', **{self._name: self.get_gte_lte_params(value, 'gt')})
        ])

    def get_filter_gte(self, value):
        return Bool(filter=[
            Q('range', **{self._name: self.get_gte_lte_params(value, 'gte')})
        ])

    def get_filter_lt(self, value):
        return Bool(filter=[Q(
            'range',
            **{self._name: self.get_gte_lte_params(value, 'lt')}
        )])

    def get_filter_lte(self, value):
        return Bool(filter=[Q(
            'range',
            **{self._name: self.get_gte_lte_params(value, 'lte')}
        )])

    def get_filter_exclude(self, value):
        __values = self.split_lookup_value(value)

        __queries = []
        for __value in __values:
            __queries.append(
                ~Q('term', **{self._name: __value})
            )

        if __queries:
            return six.moves.reduce(operator.or_, __queries)

        return None


class NestedFilteringField(FilteringFilterField):
    def __init__(self, path, field_name=None, lookups=[], **kwargs):
        super().__init__(field_name=field_name, lookups=lookups, **kwargs)
        self.path = path

    def prepare_queryset(self, queryset, context=None):  # noqa:C901
        data = context or self.context
        if not data:
            return queryset
        for lookup, value in data.items():
            func = getattr(self, 'get_filter_{}'.format(lookup), None)
            if not func:
                continue
            q = func(value)
            if q:
                queryset = queryset.query('nested', path=self.path, query=q)

        return queryset


class IdsSearchField(SearchFieldMixin, DataMixin, fields.Field):
    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset
        __ids = []
        for item in data:
            __values = self.split_lookup_value(item)
            __ids += __values

        if __ids:
            __ids = list(set(__ids))
            queryset = queryset.query(
                'ids', **{'values': __ids}
            )
        return queryset


class SuggesterFilterField(SearchFieldMixin, DataMixin, fields.Field):
    def __init__(self, field, suggesters=None, **metadata):
        self.field_name = field
        self.suggesters = suggesters if isinstance(suggesters, list) else (constants.ALL_SUGGESTERS,)
        super().__init__(**metadata)

    def prepare_data(self, name, data):
        data = dict(data)
        field_data = {k: v for k, v in data.items() if k.startswith(name)}
        data.update(FlatDict(field_data, delimiter=constants.SEPARATOR_LOOKUP_FILTER).as_dict())
        return data

    def apply_suggester_term(self, queryset, value):
        return queryset.suggest(
            self.name,
            value,
            term={'field': self.field_name}
        )

    def apply_suggester_phrase(self, queryset, value):
        return queryset.suggest(
            self.name,
            value,
            phrase={'field': self.field_name}
        )

    def apply_suggester_completion(self, queryset, value):
        return queryset.suggest(
            self.name,
            value,
            completion={'field': self.field_name}
        )

    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset
        for suggester_type, value in data.items():
            if suggester_type in self.suggesters:
                if suggester_type == constants.SUGGESTER_TERM:
                    queryset = self.apply_suggester_term(queryset, value)
                elif suggester_type == constants.SUGGESTER_PHRASE:
                    queryset = self.apply_suggester_phrase(queryset, value)
                elif suggester_type == constants.SUGGESTER_COMPLETION:
                    queryset = self.apply_suggester_completion(queryset, value)
        return queryset


class SearchFilterField(SearchFieldMixin, DataMixin, fields.Field):
    def __init__(self, search_fields=None, search_nested_fields=None, **metadata):
        self.field_names = search_fields if isinstance(search_fields, (list, tuple, dict)) else ()
        self.search_nested_fields = search_nested_fields if isinstance(search_nested_fields, dict) else {}
        super().__init__(**metadata)

    def _deserialize(self, value, attr, data):
        if isinstance(value, str):
            return [value, ]
        return value

    def construct_nested_search(self, data):
        __queries = []
        for search_term in data:
            for path, _fields in self.search_nested_fields.items():
                queries = []
                for field in _fields:
                    field_key = "{}.{}".format(path, field)
                    queries.append(
                        Q("match", **{field_key: search_term})
                    )

                __queries.append(
                    Q(
                        "nested",
                        path=path,
                        query=six.moves.reduce(operator.or_, queries)
                    )
                )

        return __queries

    def construct_search(self, data):
        __queries = []
        for search_term in data:
            __values = self.split_lookup_value(search_term, 1)
            __len_values = len(__values)
            if __len_values > 1:
                field, value = __values
                if field in self.field_names:
                    # Initial kwargs for the match query
                    field_kwargs = {field: {'query': value}}
                    # In case if we deal with structure 2
                    if isinstance(self.field_names, dict):
                        extra_field_kwargs = self.field_names[field]
                        if extra_field_kwargs:
                            field_kwargs[field].update(extra_field_kwargs)
                    # The match query
                    __queries.append(
                        Q("match", **field_kwargs)
                    )
            else:
                for field in self.field_names:
                    # Initial kwargs for the match query
                    field_kwargs = {field: {'query': search_term}}

                    # In case if we deal with structure 2
                    if isinstance(self.field_names, dict):
                        extra_field_kwargs = self.field_names[field]
                        if extra_field_kwargs:
                            field_kwargs[field].update(extra_field_kwargs)

                    # The match query
                    __queries.append(
                        Q("match", **field_kwargs)
                    )
        return __queries

    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset
        __queries = self.construct_search(data) + self.construct_nested_search(data)

        if __queries:
            queryset = queryset.query('bool', should=__queries)
        return queryset


class FacetedFilterField(SearchFieldMixin, DataMixin, fields.Field):
    def __init__(self, facets=None, **metadata):
        self.facets = facets if isinstance(facets, dict) else {}
        super().__init__(**metadata)

    def _deserialize(self, value, attr, data):
        if isinstance(value, str):
            return [value, ]
        return value

    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset

        for __field, __facet in self.facets.items():
            if __field in data:
                agg = __facet.get_aggregation()
                agg_filter = Q('match_all')

                queryset.aggs.bucket(
                    '_filter_' + __field,
                    'filter',
                    filter=agg_filter
                ).bucket(__field, agg)
        return queryset


class GeoSpatialFilteringFilterField(SearchFieldMixin, DataMixin, fields.Field):
    pass


class GeoSpatialOrderingFilterField(SearchFieldMixin, DataMixin, fields.Field):
    pass


class OrderingFilterField(SearchFieldMixin, DataMixin, fields.Field):
    ordering_param = 'sort'

    def __init__(self, ordering_fields=None, default_ordering=None, **metadata):
        self.ordering_fields = ordering_fields if isinstance(ordering_fields, dict) else {}
        self.ordering_fields['_score'] = '_score'
        self.default_ordering = default_ordering or []
        super().__init__(**metadata)

    def prepare_fields_data(self, data):
        sort_params = data or self.default_ordering
        if isinstance(sort_params, str):
            sort_params = [sort_params, ]
        __sort_params = []
        for param in sort_params:
            __key = param.lstrip('-')
            __direction = '-' if param.startswith('-') else ''
            if __key in self.ordering_fields:
                __field_name = self.ordering_fields[__key] or __key
                __sort_params.append('{}{}'.format(__direction, __field_name))
        return __sort_params

    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset

        return queryset.sort(*self.prepare_fields_data(data))


class HighlightBackend(SearchFieldMixin, DataMixin, fields.Field):
    _ALL = '_all'
    _ES_ALL_KEY = _ALL

    def __init__(self, highlight_fields=None, **metadata):
        self.highlight_fields = highlight_fields or {}
        super().__init__(**metadata)

    def prepare_fields_data(self, data):
        highlight_fields = data or []
        __params = {}
        if isinstance(highlight_fields, str):
            highlight_fields = [highlight_fields, ]

        if self._ALL in self.highlight_fields:
            __params[self._ES_ALL_KEY] = self.highlight_fields[self._ALL]
            __params[self._ES_ALL_KEY]['enabled'] = True

        for field in highlight_fields:
            if field in self.highlight_fields:
                if 'enabled' not in self.highlight_fields[field]:
                    self.highlight_fields[field]['enabled'] = False

                if 'options' not in self.highlight_fields[field]:
                    self.highlight_fields[field]['options'] = {}
                __params[field] = self.highlight_fields[field]
        return __params

    def prepare_queryset(self, queryset, context=None):
        data = context or self.context
        if not data:
            return queryset

        params = self.prepare_fields_data(data)

        for __field, __options in params.items():
            if __options['enabled']:
                queryset = queryset.highlight(__field, **__options['options'])

        return queryset

#
# class GeoSpatialFilteringFilterBackend(BaseFilterBackend, FilterBackendMixin):
#     @classmethod
#     def prepare_filter_fields(cls, resource):
#         filter_fields = getattr(resource, 'geo_spatial_filter_fields', {})
#
#         for field, options in filter_fields.items():
#             if options is None or isinstance(options, six.string_types):
#                 filter_fields[field] = {
#                     'field': options or field
#                 }
#             elif 'field' not in filter_fields[field]:
#                 filter_fields[field]['field'] = field
#
#             if 'lookups' not in filter_fields[field]:
#                 filter_fields[field]['lookups'] = tuple(
#                     constants.ALL_GEO_SPATIAL_LOOKUP_FILTERS_AND_QUERIES
#                 )
#
#         return filter_fields
#
#     @classmethod
#     def get_geo_distance_params(cls, value, field):
#         __values = cls.split_lookup_value(value, maxsplit=3)
#         __len_values = len(__values)
#
#         if __len_values < 3:
#             return {}
#
#         params = {
#             'distance': __values[0],
#             field: {
#                 'lat': __values[1],
#                 'lon': __values[2],
#             }
#         }
#
#         if __len_values == 4:
#             params['distance_type'] = __values[3]
#         else:
#             params['distance_type'] = 'sloppy_arc'
#
#         return params
#
#     @classmethod
#     def get_geo_polygon_params(cls, value, field):
#         __values = cls.split_lookup_value(value)
#         __len_values = len(__values)
#
#         if not __len_values:
#             return {}
#
#         __points = []
#         __options = {}
#
#         for __value in __values:
#             if constants.SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE in __value:
#                 __lat_lon = __value.split(
#                     constants.SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE
#                 )
#                 if len(__lat_lon) >= 2:
#                     __points.append(
#                         {
#                             'lat': float(__lat_lon[0]),
#                             'lon': float(__lat_lon[1]),
#                         }
#                     )
#
#             elif constants.SEPARATOR_LOOKUP_COMPLEX_VALUE in __value:
#                 __opt_name_val = __value.split(
#                     constants.SEPARATOR_LOOKUP_COMPLEX_VALUE
#                 )
#                 if len(__opt_name_val) >= 2:
#                     if __opt_name_val[0] in ('_name', 'validation_method'):
#                         __options.update(
#                             {
#                                 __opt_name_val[0]: __opt_name_val[1]
#                             }
#                         )
#
#         if __points:
#             params = {
#                 field: {
#                     'points': __points
#                 }
#             }
#             params.update(__options)
#
#             return params
#         return {}
#
#     @classmethod
#     def get_geo_bounding_box_params(cls, value, field):
#         __values = cls.split_lookup_value(value)
#         __len_values = len(__values)
#
#         if not __len_values:
#             return {}
#
#         __top_left_points = {}
#         __bottom_right_points = {}
#         __options = {}
#
#         # Top left
#         __lat_lon = __values[0].split(
#             constants.SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE
#         )
#         if len(__lat_lon) >= 2:
#             __top_left_points.update({
#                 'lat': float(__lat_lon[0]),
#                 'lon': float(__lat_lon[1]),
#             })
#
#         # Bottom right
#         __lat_lon = __values[1].split(
#             constants.SEPARATOR_LOOKUP_COMPLEX_MULTIPLE_VALUE
#         )
#         if len(__lat_lon) >= 2:
#             __bottom_right_points.update({
#                 'lat': float(__lat_lon[0]),
#                 'lon': float(__lat_lon[1]),
#             })
#
#         # Options
#         for __value in __values[2:]:
#             if constants.SEPARATOR_LOOKUP_COMPLEX_VALUE in __value:
#                 __opt_name_val = __value.split(
#                     constants.SEPARATOR_LOOKUP_COMPLEX_VALUE
#                 )
#                 if len(__opt_name_val) >= 2:
#                     if __opt_name_val[0] in ('_name',
#                                              'validation_method',
#                                              'type'):
#                         __options.update(
#                             {
#                                 __opt_name_val[0]: __opt_name_val[1]
#                             }
#                         )
#
#         if not __top_left_points or not __bottom_right_points:
#             return {}
#
#         params = {
#             field: {
#                 'top_left': __top_left_points,
#                 'bottom_right': __bottom_right_points,
#             }
#         }
#         params.update(__options)
#
#         return params
#
#     @classmethod
#     def apply_query_geo_distance(cls, queryset, options, value):
#         return queryset.query(
#             Q(
#                 'geo_distance',
#                 **cls.get_geo_distance_params(value, options['field'])
#             )
#         )
#
#     @classmethod
#     def apply_query_geo_polygon(cls, queryset, options, value):
#         return queryset.query(
#             Q(
#                 'geo_polygon',
#                 **cls.get_geo_polygon_params(value, options['field'])
#             )
#         )
#
#     @classmethod
#     def apply_query_geo_bounding_box(cls, queryset, options, value):
#         return queryset.query(
#             Q(
#                 'geo_bounding_box',
#                 **cls.get_geo_bounding_box_params(value, options['field'])
#             )
#         )
#
#     def get_filter_query_params(self, resource, params):
#
#         query_params = params.copy()
#
#         filter_query_params = {}
#         filter_fields = self.prepare_filter_fields(resource)
#         for query_param in query_params:
#             query_param_list = self.split_lookup_filter(
#                 query_param,
#                 maxsplit=1
#             )
#             field_name = query_param_list[0]
#
#             if field_name in filter_fields:
#                 lookup_param = None
#                 if len(query_param_list) > 1:
#                     lookup_param = query_param_list[1]
#
#                 valid_lookups = filter_fields[field_name]['lookups']
#
#                 if lookup_param is None or lookup_param in valid_lookups:
#                     values = [
#                         __value.strip()
#                         for __value
#                         in query_params.getlist(query_param)
#                         if __value.strip() != ''
#                     ]
#
#                     if values:
#                         filter_query_params[query_param] = {
#                             'lookup': lookup_param,
#                             'values': values,
#                             'field': filter_fields[field_name].get(
#                                 'field',
#                                 field_name
#                             ),
#                             'type': resource.mapping
#                         }
#         return filter_query_params
#
#     def filter_queryset(self, resource, queryset, params):
#         filter_query_params = self.get_filter_query_params(resource, params)
#         for options in filter_query_params.values():
#
#             # For all other cases, when we don't have multiple values,
#             # we follow the normal flow.
#             for value in options['values']:
#
#                 # `geo_distance` query lookup
#                 if options['lookup'] == constants.LOOKUP_FILTER_GEO_DISTANCE:
#                     queryset = self.apply_query_geo_distance(
#                         queryset,
#                         options,
#                         value
#                     )
#
#                 # `geo_polygon` query lookup
#                 elif options['lookup'] == constants.LOOKUP_FILTER_GEO_POLYGON:
#                     queryset = self.apply_query_geo_polygon(
#                         queryset,
#                         options,
#                         value
#                     )
#
#                 # `geo_bounding_box` query lookup
#                 elif options['lookup'] == constants.LOOKUP_FILTER_GEO_BOUNDING_BOX:
#                     queryset = self.apply_query_geo_bounding_box(
#                         queryset,
#                         options,
#                         value
#                     )
#
#         return queryset
#
#
# class GeoSpatialOrderingFilterBackend(BaseFilterBackend, FilterBackendMixin):
#     ordering_param = constants.GEO_DISTANCE_ORDERING_PARAM
#
#     @classmethod
#     def get_geo_distance_params(cls, value, field):
#         __values = cls.split_lookup_value(value, maxsplit=3)
#         __len_values = len(__values)
#
#         if __len_values < 2:
#             return {}
#
#         params = {
#             field: {
#                 'lat': __values[0],
#                 'lon': __values[1],
#             }
#         }
#
#         if __len_values > 2:
#             params['unit'] = __values[2]
#         else:
#             params['unit'] = 'm'
#         if __len_values > 3:
#             params['distance_type'] = __values[3]
#         else:
#             params['distance_type'] = 'sloppy_arc'
#
#         return params
#
#     def get_ordering_query_params(self, resource, params):
#         query_params = params.copy()
#         ordering_query_params = query_params.get(self.ordering_param, [])
#         __ordering_params = []
#         # Remove invalid ordering query params
#         for query_param in ordering_query_params:
#             __key, __value = FilterBackendMixin.split_lookup_value(
#                 query_param.lstrip('-'),
#                 maxsplit=1,
#             )
#             __direction = 'desc' if query_param.startswith('-') else 'asc'
#             if __key in resource.geo_spatial_ordering_fields:
#                 __field_name = resource.geo_spatial_ordering_fields[__key] or __key
#                 __params = self.get_geo_distance_params(__value, __field_name)
#                 __params['order'] = __direction
#                 __ordering_params.append(__params)
#
#         return __ordering_params
#
#     def filter_queryset(self, resource, queryset, params):
#         ordering_query_params = self.get_ordering_query_params(resource, params)
#
#         if ordering_query_params:
#             return queryset.sort(*ordering_query_params)
#
#         return queryset
