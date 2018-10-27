# -*- coding: utf-8 -*-

import collections
import datetime
import itertools
import uuid

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError
from elasticsearch.helpers import streaming_bulk

from mcod.lib.search import mappers


class ElasticsearchStorage(object):
    def __init__(self, es=None):
        self.__es = es if es is not None else Elasticsearch()

    def __repr__(self):
        template = 'Storage {engine}'
        text = template.format(engine=self.__es)
        return text

    @property
    def indexes(self, prefix='resource_'):
        idxs = self.__es.indices.get_alias('%s*' % prefix)
        for index_name, index in idxs.items():
            for alias_name in index.get('aliases', {}).keys():
                yield alias_name

    def get_real_index_name(self, index_name):
        uid = str(uuid.uuid4())[:8]
        today = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        return '{}_{}_{}'.format(index_name, today, uid)

    def create_index(self, index_name, index_settings=None):
        if not index_settings:
            index_settings = {
                'number_of_shards': 1,
                'number_of_replicas': 1
            }
        real_index_name = self.get_real_index_name(index_name)
        body = None
        if index_settings is not None:
            body = dict(
                settings=index_settings
            )
        self.__es.indices.create(real_index_name, body=body)
        self.__es.indices.put_alias(real_index_name, index_name)
        return real_index_name

    def put_mapping(self, index_name, schema, mapping_generator_cls):
        mapping = mappers.descriptor_to_mapping(
            schema, mapping_generator_cls=mapping_generator_cls
        )
        self.__es.indices.put_mapping('doc', mapping, index=index_name)

    def generate_doc_id(self, row, primary_key):
        return '/'.join([str(row.get(k)) for k in primary_key])

    def create(self, index_name, schema, reindex=False, always_recreate=False, mapping_generator_cls=None,
               index_settings=None):
        existing_index_names = []
        if self.__es.indices.exists_alias(name=index_name):
            existing_index_names = self.__es.indices.get_alias(index_name)
            existing_index_names = sorted(existing_index_names.keys())

        if len(existing_index_names) == 0 or always_recreate:
            index_name = self.create_index(index_name, index_settings=index_settings)
            self.put_mapping(index_name, schema, mapping_generator_cls)
        else:
            index_name = existing_index_names[-1]
            try:
                self.put_mapping(schema, index_name, mapping_generator_cls)
                existing_index_names.pop(-1)

            except RequestError:
                if reindex:
                    index_name = self.create_index(index_name, index_settings=index_settings)
                    self.put_mapping(index_name, schema, mapping_generator_cls)
                else:
                    raise

        if reindex and len(existing_index_names) > 0:
            reindex_body = dict(
                source=dict(
                    index=existing_index_names
                ),
                dest=dict(
                    index=index_name,
                    version_type='external'
                )
            )
            self.__es.reindex(reindex_body)
            self.__es.indices.flush()

            for existing_index_name in existing_index_names:
                self.__es.indices.delete(existing_index_name)

    def delete(self, index_name=None):
        def internal_delete(index_name):
            if self.__es.indices.exists_alias(name=index_name):
                existing_index_names = self.__es.indices.get_alias(index_name)
                existing_index_names = list(existing_index_names.keys())
                for existing_index_name in existing_index_names:
                    self.__es.indices.delete(existing_index_name)

        if index_name is None:
            for index_name in self.indexes:
                internal_delete(index_name)
        else:
            internal_delete(index_name)

    def describe(self, index_name, descriptor=None):
        raise NotImplementedError()

    def iter(self, index_name):
        from_ = 0
        size = 100
        done = False
        while not done:
            results = self.__es.search(index=index_name,
                                       from_=from_,
                                       size=size)
            hits = results.get('hits', {}).get('hits', [])
            for source in hits:
                yield source.get('_source')
            done = len(hits) == 0
            from_ += size

    def read(self, bucket):
        return list(self.iter(bucket))

    def write(self, index_name, rows, update=True, as_generator=False):
        def actions(rows_, update_):
            if update_:
                for idx, row_ in enumerate(rows_):
                    yield {
                        '_op_type': 'update',
                        '_index': index_name,
                        '_type': 'doc',
                        '_id': idx,
                        '_source': {
                            'doc': row_,
                            'doc_as_upsert': True
                        }
                    }

            else:
                for idx, row_ in enumerate(rows_):
                    yield {
                        '_op_type': 'index',
                        '_index': index_name,
                        '_type': 'doc',
                        '_id': idx,
                        '_source': row_
                    }

        iterables = itertools.tee(rows)
        actions_iterable = actions(iterables[0], update)
        iter = zip(streaming_bulk(self.__es, actions=actions_iterable), iterables[1])

        if as_generator:
            for result, row in iter:
                yield row
        else:
            collections.deque(iter, maxlen=0)

        self.__es.indices.flush(index_name)
