from django.core.cache import caches

from mcod import settings


def flush_sessions():
    _cache = caches[settings.SESSION_CACHE_ALIAS]
    _cache.delete_pattern('*')


def flush_cache():
    _cache = caches["default"]
    _cache.delete_pattern('*')
