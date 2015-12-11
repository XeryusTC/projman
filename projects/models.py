# -*- coding: utf-8
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

INVALID_USER_ERROR = _('Actions and projects must belong to the same user.')

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
    project = models.ForeignKey('Project', blank=True, null=True, default=None,
        related_name='action_list')

    def clean(self):
        # Do not allow the user field to be different than the project's
        # user field
        if self.project != None and self.user != self.project.user:
            raise ValidationError(INVALID_USER_ERROR)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = ('text', 'user')


class Project(models.Model):
    name = models.CharField(max_length=64, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    description = models.CharField(max_length=1024, default='', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'user')
