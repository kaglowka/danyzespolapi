from django.contrib import admin

# Register your models here.
from mcod.searchhistories.models import SearchHistory


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    pass
