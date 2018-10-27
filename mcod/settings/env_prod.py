from mcod.settings.base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ['*']

env = environ.Env()  # noqa: F405

DATABASES = {
    'default': env.db('POSTGRES_DATABASE_URL', default='postgres:///mcod'),  # noqa: F405
}
DATABASES['default']['ATOMIC_REQUESTS'] = True

TEMPLATES[0]['OPTIONS']['debug'] = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env('EMAIL_PORT', default=25)
EMAIL_USE_TLS = True if env('EMAIL_USE_TLS', default=0) in ('yes', 1, 'true') else False
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')

NO_REPLY_EMAIL = 'no-reply@dane.gov.pl'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

REDIS_URL = env('REDIS_URL', default='redis://mcod-redis:6379')

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "%s/1" % REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "%s/2" % REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }

}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

BASE_URL = 'https://www.dane.gov.pl'
PASSWORD_RESET_URL = 'https://www.dane.gov.pl/user/reset-password/%s/'
EMAIL_VALIDATION_URL = 'https://www.dane.gov.pl/user/verify-email/%s/'

PREVIEW_LINK_BASE = "https://www.dane.gov.pl/"

ELASTICSEARCH_HOSTS = env('ELASTICSEARCH_HOSTS',
                          default='mcod-elasticsearch-1:9200,' \
                                  'mcod-elasticsearch-2:9200,' \
                                  'mcod-elasticsearch-3:9200,' \
                                  'mcod-elasticsearch-4:9200,' \
                                  'mcod-elasticsearch-5:9200,' \
                                  'mcod-elasticsearch-6:9200')

ELASTICSEARCH_DSL = {
    'default': {
        'hosts': ELASTICSEARCH_HOSTS.split(','),
        'http_auth': "user:changeme",
        'timeout': 100
    },
}
CELERY_BROKER_URL = 'amqp://%s' % str(env('RABBITMQ_HOST', default='mcod-rabbitmq:5672'))
