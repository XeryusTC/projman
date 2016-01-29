# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20160123_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionlistitem',
            name='deadline',
            field=models.DateTimeField(default=None, null=True, blank=True),
        ),
    ]
