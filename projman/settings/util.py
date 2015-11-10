# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
import os

def get_env_setting(setting):
    try:
        return os.environ[setting]
    except KeyError:
        raise ImproperlyConfigured(
            "Could not find setting '{}' in the environment.".format(setting))
