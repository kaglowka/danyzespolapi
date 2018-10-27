from mcod.settings.base import *  # noqa: F403, F405

ROOT_DIR = environ.Path(__file__) - 3  # noqa: F405

DEBUG = True

env = environ.Env()  # noqa: F405

# Use this only for vagrant
# env_file = str(ROOT_DIR.path('.env'))  # noqa: F405
# env.read_env(env_file)

DATABASES = {
    'default': env.db('POSTGRES_DATABASE_URL', default='postgres://mcod:mcod@127.0.0.1:5432/mcod'),  # noqa: F405
}

DATABASES['default']['ATOMIC_REQUESTS'] = True

TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa: F405

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'  # change this to a proper location

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REDIS_URL = env('REDIS_URL', default='redis://127.0.0.1:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "%s/0" % REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "%s/1" % REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

PASSWORD_RESET_URL = 'http://api.test.test/user/reset-password/%s/'
EMAIL_VALIDATION_URL = 'http://api.test.test/user/verify-email/%s/'


PREVIEW_LINK_BASE = "http://www.dane.gov.pl/"


ELASTICSEARCH_HOSTS = env('ELASTICSEARCH_HOSTS', default='mcod-elasticsearch-1:9200')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_HOSTS.split(','),
        'http_auth': "user:changeme",
        'timeout': 100
    },
}

ELASTICSEARCH_INDEX_NAMES = {
    "articles": "articles_test",
    "applications": "applications_test",
    "datasets": "datasets_test",
    "institutions": "institutions_test",
    "resources": "resources_test",
    "histories": "histories_test",
    "searchhistories": "searchhistories_test",
}

MEDIA_ROOT = str(ROOT_DIR('test-data/test/media'))
IMAGES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, 'images'))
RESOURCES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, 'resources'))

MEDIA_URL = '/test/media/'
RESOURCES_URL = '%s%s' % (MEDIA_URL, 'resources')
IMAGES_URL = '%s%s' % (MEDIA_URL, 'images')

CELERY_TASK_ALWAYS_EAGER = True

CELERY_TASK_DEFAULT_QUEUE = 'mcod'

CELERY_TASK_QUEUES = {
    Queue('test'),
}

CELERY_TASK_ROUTES = {
}

CELERY_BROKER_URL = 'amqp://%s' % str(env('RABBITMQ_HOST', default='mcod-rabbitmq:5672'))

