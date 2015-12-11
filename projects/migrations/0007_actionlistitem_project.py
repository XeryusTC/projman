# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_auto_20151210_1345'),
    ]

    operations = [
        migrations.AddField(
            model_name='actionlistitem',
            name='project',
            field=models.ForeignKey(null=True, related_name='action_list', to='projects.Project', default=None, blank=True),
        ),
    ]
