# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0002_settings_inlist_delete_confirm'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='action_delete_confirm',
            field=models.BooleanField(default=True),
        ),
    ]
