import json

import marshmallow as ma
import marshmallow_jsonapi as ja

from mcod.lib.serializers import BasicSerializer


class HistorySchema(ja.Schema):
    id = ma.fields.Int(dump_only=True)
    table_name = ma.fields.Str()
    row_id = ma.fields.Int()
    action = ma.fields.Str()
    # old_value = ma.fields.Str()
    new_value = ma.fields.Dict()
    difference = ma.fields.Dict()
    change_user_id = ma.fields.Str()
    change_timestamp = ma.fields.DateTime()
    message = ma.fields.Str()

    class Meta:
        type_ = "history"
        strict = True
        self_url_many = '/histories'
        self_url = "/histories/{history_id}"
        self_url_kwargs = {"history_id": "<id>"}


class HistorySerializer(HistorySchema, BasicSerializer):

    def new_value_to_obj(self, obj):
        new_value = json.loads(obj.new_value)
        if new_value.get('password'):
            new_value['password'] = "**********"
        return new_value

    def difference_to_obj(self, obj):
        difference = json.loads(obj.difference)
        if difference.get("values_changed"):
            if difference['values_changed'].get("root['password']"):
                difference['values_changed']["root['password']"]['new_value'] = "********"
                difference['values_changed']["root['password']"]['old_value'] = "********"
        return difference

    new_value = ma.fields.Method('new_value_to_obj')
    difference = ma.fields.Method('difference_to_obj')

    class Meta:
        type_ = "history"
        strict = True
        self_url_many = '/histories'
        self_url = "/histories/{history_id}"
        self_url_kwargs = {"history_id": "<id>"}
