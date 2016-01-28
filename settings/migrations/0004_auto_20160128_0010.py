# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0003_settings_action_delete_confirm'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='settings',
            name='id',
        ),
        migrations.AlterField(
            model_name='settings',
            name='user',
            field=models.OneToOneField(default=None, primary_key=True, to=settings.AUTH_USER_MODEL, related_name='settings', serialize=False),
        ),
    ]
