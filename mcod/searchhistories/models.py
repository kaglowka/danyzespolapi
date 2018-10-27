from django.db import models

from mcod.lib.model_mixins import IndexableMixin
from mcod.lib.model_utils import TimeStampedModel


class SearchHistory(IndexableMixin, TimeStampedModel):
    url = models.URLField(max_length=512)
    query_sentence = models.CharField(max_length=256)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
