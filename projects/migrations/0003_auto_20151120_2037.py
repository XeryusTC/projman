# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20151117_1710'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inlistitem',
            options={'ordering': ('pk',)},
        ),
    ]
