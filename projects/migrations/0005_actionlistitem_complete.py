# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_auto_20151121_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionlistitem',
            name='complete',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]
