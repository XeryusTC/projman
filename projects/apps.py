# -*- coding:utf-8 -*-
from django.apps import AppConfig

class ProjectConfig(AppConfig):
    name = 'projects'
    def ready(self):
        import projects.signals
