# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, default=None,
        related_name='settings')
    language = models.CharField(max_length=5, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE)

    def __str__(self):
        return str(self.user) + "'s settings"
