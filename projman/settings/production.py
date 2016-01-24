# -*- coding: utf-8 -*-
from .base import *
from .util import get_env_setting

DEBUG = False
DOMAIN = get_env_setting('PROJMAN_DOMAIN')
ALLOWED_HOSTS = [
    DOMAIN,
    'www.' + DOMAIN,
]

SECRET_KEY = get_env_setting('PROJMAN_SECRET_KEY')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': get_env_setting('PROJMAN_DB_NAME'),
        'USER': get_env_setting('PROJMAN_DB_USER'),
        'PASSWORD': get_env_setting('PROJMAN_DB_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '',
    },
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.child('templates'),],
        'OPTIONS': {
            'context_processors': context_processors,
            'loaders': [
                ('django.template.loaders.cached.Loader', [
                    'django.template.loaders.filesystem.Loader',
                    'django.template.loaders.app_directories.Loader',
                ]),
            ],
        },
    },
]

SITE_ID = 1

INSTALLED_APPS += ('gunicorn',)

SOCIALACCOUNT_PROVIDERS = {
    'persona': {
        'AUDIENCE': DOMAIN
    }
}

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = get_env_setting('PROJMAN_EMAIL_HOST')
EMAIL_PORT = get_env_setting('PROJMAN_EMAIL_PORT')
EMAIL_HOST_PASSWORD = get_env_setting('PROJMAN_EMAIL_HOST_PASSWORD')
EMAIL_HOST_USER = get_env_setting('PROJMAN_EMAIL_HOST_USER')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
EMAIL_USE_TLS = True

# Security settings
X_FRAME_OPTIONS = 'DENY'
# Currently disabled since we don't have staging specific settings yet
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

try:
    from .admins import ADMINS
except ImportError:
    # No admins have been configured, ignore them
    pass
