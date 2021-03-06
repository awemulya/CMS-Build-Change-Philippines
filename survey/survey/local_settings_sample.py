from .settings import *
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'survey',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        }
}

INSTALLED_APPS += [

    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]
#
# WEBPACK_LOADER = {
#     'DEFAULT': {
#         'CACHE': False,
#         'BUNDLE_DIR_NAME': '/dist/',#('/build/' if DEBUG else '/dist/'),
#         # 'BUNDLE_DIR_NAME': '/build/',#('/build/' if DEBUG else '/dist/'),
#         'STATS_FILE': os.path.join(settings.BASE_DIR, 'webpack-stats.json'),
#         # 'STATS_FILE': os.path.join(settings.BASE_DIR, 'webpack-stats-local.json'),
#     }
# }
#
# INTERNAL_IPS = '127.0.0.1'