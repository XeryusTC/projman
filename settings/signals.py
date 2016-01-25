# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from settings import models

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_settings_for_new_user(sender, created, instance, **kwargs):
    if created:
        p = models.Settings(user=instance)
        p.save()
