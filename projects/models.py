# -*- coding: utf-8
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _

DUPLICATE_ACTION_ERROR = _("You already planned to do this")
INVALID_USER_ERROR = _('Actions and projects must belong to the same user.')
ACTION_PROJECT_NAME = 'Actions' # Don't translate this (yet)

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
    project = models.ForeignKey('Project', default=None, null=True,
        related_name='action_list')

    def clean(self):
        # Do not allow the user field to be different than the project's
        # user field
        if self.project != None and self.user != self.project.user:
            raise ValidationError(INVALID_USER_ERROR)

        # Make the default project the user's Actions project
        if self.project == None:
            self.project = Project.objects.get(user=self.user,
                name=ACTION_PROJECT_NAME)

        # Validate that two items on the list are not the same
        queryset = ActionlistItem.objects.exclude(pk=self.pk).filter(
            text=self.text, user=self.user, project=self.project)
        if queryset.exists():
            raise ValidationError(DUPLICATE_ACTION_ERROR)

    def save(self, *args, **kwargs):
        # Just changing the default in clean is not enough, we need to
        # change it here as well
        if self.project == None:
            self.project = Project.objects.get(user=self.user,
                name=ACTION_PROJECT_NAME)
        super(ActionlistItem, self).save(*args, **kwargs)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = (('text', 'user', 'project'),)


class Project(models.Model):
    name = models.CharField(max_length=64, default='')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    description = models.CharField(max_length=1024, default='', blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ('name', 'user')


def get_user_action_project(user):
    return Project.objects.get(user=user, name=ACTION_PROJECT_NAME)
