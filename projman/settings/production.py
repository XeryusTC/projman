# -*- coding: utf-8 -*-
from .base import *

DEBUG = False
DOMAIN = get_env_setting('PROJMAN_DOMAIN')
ALLOWED_HOSTS = [
    DOMAIN,
    'www.' + DOMAIN,
]

SECRET_KEY = get_env_setting('PROJMAN_SECRET_KEY')

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
        },
    },
]

SITE_ID = 1
