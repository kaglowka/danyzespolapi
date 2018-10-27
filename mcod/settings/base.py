from collections import OrderedDict

import environ
import os
from django.utils.translation import gettext_lazy as _
from kombu import Queue

ROOT_DIR = environ.Path(__file__) - 3

APPS_DIR = ROOT_DIR.path('mcod')

DATA_DIR = ROOT_DIR.path('data')

LOGS_DIR = str(ROOT_DIR.path('logs'))

DATABASE_DIR = str(ROOT_DIR.path('database'))

DEBUG = False

SECRET_KEY = 'xb2rTZ57yOY9iCdqR7W+UAWnU'

INSTALLED_APPS = [
    'dal',
    'dal_select2',
    'dal_admin_filters',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'suit',
    'mcod.organizations',
    'mcod.categories',
    'mcod.tags',
    'mcod.applications',
    'mcod.articles',
    'mcod.datasets',
    'mcod.resources',
    'mcod.users',
    'mcod.licenses',
    'mcod.following',
    'django_elasticsearch_dsl',
    'ckeditor',
    'ckeditor_uploader',
    'rules.apps.AutodiscoverRulesConfig',
    'nested_admin',
    'django_celery_results',
    'mcod.counters',
    'mcod.histories',
    'mcod.lib.search',
    'localflavor',
    'mcod.searchhistories',
    'mcod.core',
    'django.contrib.admin',
    # 'django_celery_beat',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    # 'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mcod.lib.middleware.PostgresConfMiddleware',
    'mcod.lib.middleware.UserTokenMiddleware',
]

ROOT_URLCONF = 'mcod.urls'

WSGI_APPLICATION = 'mcod.wsgi.application'

ALLOWED_HOSTS = []

FIXTURE_DIRS = (
    str(ROOT_DIR.path('fixtures')),
)

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

DEBUG_EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/tmp/app-messages'

ADMINS = [
    ("""Rafał Korzeniewski""", 'rafal.korzeniewski@britenet.com.pl'),
    ("""Piotr Zientarski""", 'piotr.zientarski@britenet.com.pl'),
    ("""Michał Plich""", 'michal.plich@britenet.com.pl'),
]

ADMIN_URL = r'^$'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

PASSWORD_HASHERS = [

    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'mcod.lib.hashers.PBKDF2SHA512PasswordHasher',

]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {'user_attributes': ('email', 'fullname'), 'max_similarity': 0.6}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8}
    },
    {
        'NAME': 'mcod.lib.password_validators.McodPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        'OPTIONS': {'password_list_path': str(DATA_DIR.path('common-passwords.txt.gz'))}
    },
]

AUTHENTICATION_BACKENDS = [
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend'
]

# pwgen -ny 64
JWT_SECRET_KEY = 'aes_oo7ooSh8phiayohvah0ZieH3ailahh9ieb6ahthah=hing7AhJu7eexeiHoo'
JWT_ISS = 'Ministry of Digital Affairs'
JWT_AUD = 'dane.gov.pl'
JWT_ALGORITHMS = ['HS256', ]
JWT_VERIFY_CLAIMS = ['signature', 'exp', 'nbf', 'iat']
JWT_REQUIRED_CLAIMS = ['exp', 'iat', 'nbf']
JWT_HEADER_PREFIX = 'Bearer'
JWT_LEEWAY = 0
JWT_EXPIRATION_DELTA = 24 * 60 * 60

AUTH_USER_MODEL = 'users.User'

TIME_ZONE = 'Europe/Warsaw'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            'debug': False,
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

FORM_RENDERER = 'mcod.lib.forms.renderers.TemplatesRenderer'

STATIC_ROOT = str(ROOT_DIR('statics'))
STATIC_URL = '/static/'
STATICFILES_FINDERS = [
    'mcod.lib.staticfiles_finders.StaticRootFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_ROOT = str(ROOT_DIR('media'))
IMAGES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, 'images'))
RESOURCES_MEDIA_ROOT = str(ROOT_DIR.path(MEDIA_ROOT, 'resources'))
#
# if not os.path.exists(RESOURCES_MEDIA_ROOT):
#     os.makedirs(RESOURCES_MEDIA_ROOT)
#
# if not os.path.exists(IMAGES_MEDIA_ROOT):
#     os.makedirs(IMAGES_MEDIA_ROOT)

MEDIA_URL = '/media/'
RESOURCES_URL = '%s%s' % (MEDIA_URL, 'resources')
IMAGES_URL = '%s%s' % (MEDIA_URL, 'images')

FRONTEND_URL = 'http://localhost'

CKEDITOR_UPLOAD_PATH = 'ckeditor/'

LOCALE_PATHS = (
    str(ROOT_DIR('translations')),
)

LANGUAGE_CODE = 'pl'

LANGUAGES = [
    ('pl', _('Polish')),
    ('en', _('English')),
]

REST_APISPEC_START_LINE = '---rest---'
RPC_APISPEC_START_LINE = '---rpc---'

DEFAULT_PAGE_SIZE = 20

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/0",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }

}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "sessions"

USER_STATE_CHOICES = (
    ('active', _('Active')),
    ('pending', _('Pending')),
    ('blocked', _('Blocked'))
)

USER_STATE_LIST = [choice[0] for choice in USER_STATE_CHOICES]

SUIT_CONFIG = {
    'ADMIN_NAME': _("Open Data - Administration Panel"),
    'HEADER_DATE_FORMAT': 'l, j. F Y',
    'HEADER_TIME_FORMAT': 'H:i',  # 18:42
    'SHOW_REQUIRED_ASTERISK': True,
    'CONFIRM_UNSAVED_CHANGES': True,
    'SEARCH_URL': '',
    'MENU_OPEN_FIRST_CHILD': True,  # Default True
    'MENU_EXCLUDE': ('auth.group',),
    'MENU': (
        {'label': 'Dane', 'models': [
            {'model': 'datasets.dataset', 'label': _('Datasets'), 'icon': 'icon-database'},
            {'model': 'resources.resource', 'label': _('Resources'), 'icon': 'icon-file-cloud'},
            {'model': 'organizations.organization', 'label': _('Institutions'), 'icon': 'icon-building'},
            {'model': 'applications.application', 'permissions': 'auth.add_user', 'label': _('Applications'),
             'icon': 'icon-cupe-black'},
            {'model': 'articles.article', 'label': _('Articles'), 'permissions': 'auth.add_user', 'icon': 'icon-leaf'},
        ], 'icon': 'icon-file'},
        {'label': _('Users'), 'url': '/users/user', 'icon': 'icon-lock'},

    ),

    'LIST_PER_PAGE': 20,
}

SPECIAL_CHARS = ' !"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'

CKEDITOR_CONFIGS = {
    'default': {
        # 'toolbar': 'Basic',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter',
             'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['Attachments', ],
            ['RemoveFormat', 'Source']
        ],
        'height': 300,
        'width': '100%',
    },
}

CKEDITOR_ALLOW_NONIMAGE_FILES = True

TOKEN_EXPIRATION_TIME = 24  # In hours

BASE_URL = 'https://www.dane.gov.pl'

NO_REPLY_EMAIL = 'no-reply@dane.gov.pl'
CONTACT_MAIL = 'kontakt@dane.gov.pl'

PASSWORD_RESET_URL = 'http://www.dane.gov.pl/user/reset-password/%s/'
EMAIL_VALIDATION_URL = 'http://www.dane.gov.pl/user/verify-email/%s/'

PER_PAGE_LIMIT = 200
PER_PAGE_DEFAULT = 20

ELASTICSEARCH_INDEX_NAMES = OrderedDict({
    "articles": "articles",
    "applications": "applications",
    "institutions": "institutions",
    "datasets": "datasets",
    "resources": "resources",
    "searchhistories": "searchhistories",
    "histories": "histories",
})

ELASTICSEARCH_DSL_SIGNAL_PROCESSOR = 'mcod.lib.search.signals.AsyncSignalProcessor'

ELASTICSEARCH_DEFAULT_INDEX_SETTINGS = {
    'number_of_shards': 1,
    'number_of_replicas': 1
}

PREVIEW_LINK_BASE = "http://www.dane.gov.pl/"

CELERY_RESULT_BACKEND = 'django-db'
CELERY_TASK_ALWAYS_EAGER = False

CELERY_TASK_DEFAULT_QUEUE = 'default'

CELERY_TASK_QUEUES = {
    Queue('default'),
    Queue('resources'),
    Queue('indexing'),
    Queue('periodic'),
    Queue('notifications'),
    Queue('search_history'),
}

CELERY_TASK_ROUTES = {
    'mcod.lib.search.tasks.update_document': {'queue': 'indexing'},
    'mcod.lib.search.tasks.update_with_related': {'queue': 'indexing'},
    'mcod.lib.search.tasks.delete_document': {'queue': 'indexing'},
    'mcod.lib.search.tasks.delete_with_related': {'queue': 'indexing'},
    'mcod.lib.search.tasks.pre_delete_document': {'queue': 'indexing'},
    'mcod.resources.tasks.get_resource_from_url': {'queue': 'resources'},
    'mcod.resources.tasks.process_resource_file': {'queue': 'resources'},
    'mcod.resources.tasks.process_file_data': {'queue': 'resources'},
    'mcod.counters.tasks.save_counters': {'queue': 'periodic'},
    'mcod.histories.tasks.index_history': {'queue': 'periodic'},
    'mcod.datasets.tasks.send_dataset_comment': {'queue': 'notifications'},
    'mcod.searchhistories.tasks.create_search_history': {'queue': 'search_history'},
}

RESOURCE_MIN_FILE_SIZE = 1024
RESOURCE_MAX_FILE_SIZE = 1024 * 1024 * 512  # 512MB

FIXTURE_DIRS = [
    str(ROOT_DIR('fixtures')),
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'console': {
            'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        },
        'standard': {
            'format': '[%(asctime)s][%(levelname)s] %(message)s',
        },

    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
        'django_debug': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': LOGS_DIR + "/django_debug.log",
        },
        'django_5XX': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'filename': LOGS_DIR + "/django_5XX.log",
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
        'mcod_debug': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': LOGS_DIR + "/mcod_debug.log",
        },
        'resource_file_processing': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'filename': LOGS_DIR + "/resource_file_processing.log",
            'formatter': 'standard'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['django_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'django_5XX'],
            'level': 'ERROR',
            'propagate': False,
        },
        'mcod': {
            'handlers': ['mcod_debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'resource_file_processing': {
            'handlers': ['resource_file_processing'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

SUPPORTED_CONTENT_TYPES = [
    # (family, type, extensions, openness score)
    ('application', 'csv', ('csv',), 3),
    ('application', 'epub+zip', ('epub',), 1),
    ('application', 'excel', ('xls',), 2),
    ('application', 'gml+xml', ('xml',), 3),
    ('application', 'gzip', ('gz',), 1),
    ('application', 'json', ('json',), 3),
    ('application', 'mspowerpoint', ('ppt', 'pot', 'ppa', 'pps', 'pwz'), 1),
    ('application', 'msword', ('doc', 'docx', 'dot', 'wiz'), 1),
    ('application', 'pdf', ('pdf',), 1),
    ('application', 'postscript', ('pdf', 'ps'), 1),
    ('application', 'powerpoint', ('ppt', 'pot', 'ppa', 'pps', 'pwz'), 1),
    ('application', 'rtf', ('rtf',), 1),
    ('application', 'vnd.ms-excel', ('xls', 'xlsx', 'xlb'), 2),
    ('application', 'vnd.ms-excel.12', ('xls', 'xlsx', 'xlb'), 2),
    ('application', 'vnd.ms-excel.sheet.macroEnabled.12', ('xls', 'xlsx', 'xlb'), 2),
    ('application', 'vnd.ms-powerpoint', ('ppt', 'pot', 'ppa', 'pps', 'pwz'), 1),
    ('application', 'vnd.ms-word', ('doc', 'docx', 'dot', 'wiz'), 1),
    ('application', 'vnd.oasis.opendocument.chart', ('odc',), 1),
    ('application', 'vnd.oasis.opendocument.formula', ('odf',), 3),
    ('application', 'vnd.oasis.opendocument.graphics', ('odg',), 3),
    ('application', 'vnd.oasis.opendocument.image', ('odi',), 2),
    ('application', 'vnd.oasis.opendocument.presentation', ('odp',), 1),
    ('application', 'vnd.oasis.opendocument.spreadsheet', ('ods',), 3),
    ('application', 'vnd.oasis.opendocument.text', ('odt',), 1),
    ('application', 'vnd.openxmlformats-officedocument.presentationml.presentation', ('pptx',), 1),
    ('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet', ('xlsx',), 2),
    ('application', 'vnd.openxmlformats-officedocument.wordprocessingml.document', ('docx',), 1),
    ('application', 'vnd.rar', ('rar',), 1),
    ('application', 'vnd.visio', ('vsd',), 1),
    ('application', 'x-7z-compressed', ('7zip',), 1),
    ('application', 'x-abiword', ('abw',), 1),
    ('application', 'x-bzip', ('bz',), 1),
    ('application', 'x-bzip2', ('bz2',), 1),
    ('application', 'x-csv', ('csv',), 3),
    ('application', 'x-excel', ('xls', 'xlsx', 'xlb'), 2),
    ('application', 'x-rtf', ('rtf',), 1),
    ('application', 'x-tar', ('tar',), 1),
    ('application', 'x-zip-compressed', ('zip',), 1),
    ('application', 'xhtml+xml', ('html', 'htm'), 3),
    ('application', 'xml', ('xml',), 3),
    ('application', 'zip', ('zip',), 1),
    ('application', 'x-tex', ('tex',), 3),
    ('application', 'x-texinfo', ('texi', 'texinfo',), 3),
    ('image', 'bmp', ('bmp',), 2),
    ('image', 'gif', ('gif',), 2),
    ('image', 'jpeg', ('jpeg', 'jpg', 'jpe'), 3),
    ('image', 'png', ('png',), 3),
    ('image', 'svg+xml', ('svg',), 3),
    ('image', 'tiff', ('tiff',), 2),
    ('image', 'webp', ('webp',), 2),
    ('image', 'x-tiff', ('tiff',), 2),
    ('image', 'x-xbitmap', ('xbm'), 2),
    ('image', 'x-ms-bmp', ('bmp',), 2),
    ('image', 'x-portable-pixmap', ('ppm',), 2),
    ('image', 'x-xbitmap', ('xbm',), 2),
    ('text', 'csv', ('csv',), 3),
    ('text', 'html', ('html', 'htm'), 3),
    ('text', 'xhtml+xml', ('html', 'htm'), 3),
    ('text', 'plain', ('txt', 'rd', 'md', 'csv', 'tsv', 'bat'), 3),
    ('text', 'richtext', ('rtf',), 1),
    ('text', 'tab-separated-values', ('tsv',), 3),
    ('text', 'xml', ('xml', 'wsdl', 'xpdl', 'xsl'), 3),
    ('text', 'rdf', ('rdf', 'n3', 'nt', 'trix', 'rdfa', 'xml'), 4)
]

PREVIEW_LINK_BASE = BASE_URL

FILE_UPLOAD_MAX_MEMORY_SIZE = 500000000
FILE_UPLOAD_PERMISSIONS = 0o644
