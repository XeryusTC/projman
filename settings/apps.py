# -*- coding: utf-8 -*-
from django.apps import AppConfig

class SettingsConfig(AppConfig):
    name = 'settings'

    def ready(self):
        import settings.signals
