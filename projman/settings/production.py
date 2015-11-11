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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.i18n',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'landing.context_processors.site',
            ],
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

# Security settings
X_FRAME_OPTIONS = 'DENY'
# Currently disabled since we don't have staging specific settings yet
#SESSION_COOKIE_SECURE = True
#CSRF_COOKIE_SECURE = True
