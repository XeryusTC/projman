# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('language', models.CharField(choices=[('en', 'English'), ('nl', 'Dutch')], default='en-us', max_length=5)),
                ('user', models.OneToOneField(default=None, related_name='settings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
