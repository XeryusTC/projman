# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models

class Settings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, default=None,
        related_name='settings', primary_key=True)
    language = models.CharField(max_length=5, choices=settings.LANGUAGES,
        default=settings.LANGUAGE_CODE)
    inlist_delete_confirm = models.BooleanField(default=True)
    action_delete_confirm = models.BooleanField(default=True)

    def __str__(self):
        return str(self.user) + "'s settings"
