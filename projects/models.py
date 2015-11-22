# -*- coding: utf-8
from django.conf import settings
from django.db import models

class InlistItem(models.Model):
    text = models.CharField(max_length=255, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('text', 'user')
        ordering = ('pk',)


class ActionlistItem(models.Model):
    text = models.CharField(max_length=255, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    complete = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('text', 'user')
