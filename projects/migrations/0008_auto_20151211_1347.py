# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_actionlistitem_project'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='actionlistitem',
            unique_together=set([('text', 'user', 'project')]),
        ),
    ]
