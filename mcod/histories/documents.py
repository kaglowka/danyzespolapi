# from django.apps import apps
import json
from django_elasticsearch_dsl import DocType, Index, fields
from mcod.histories.models import History
from mcod import settings

INDEX = Index(settings.ELASTICSEARCH_INDEX_NAMES['histories'])
INDEX.settings(
    number_of_shards=3,
    number_of_replicas=1
)


@INDEX.doc_type
class HistoriesDoc(DocType):
    id = fields.IntegerField()
    table_name = fields.TextField()
    row_id = fields.IntegerField()
    action = fields.TextField()
    # old_value = fields.TextField()
    new_value = fields.TextField()
    difference = fields.TextField(attr='difference')
    change_user_id = fields.IntegerField()
    change_timestamp = fields.DateField()
    message = fields.TextField()

    class Meta:
        doc_type = 'history'
        model = History

    def prepare_new_value(self, instance):
        return json.dumps(instance.new_value)
