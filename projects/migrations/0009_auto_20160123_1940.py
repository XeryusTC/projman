# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_auto_20151211_1347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actionlistitem',
            name='project',
            field=models.ForeignKey(default=None, null=True, to='projects.Project', related_name='action_list'),
        ),
    ]
