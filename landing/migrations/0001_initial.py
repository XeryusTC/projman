# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def setup_site(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model('sites', 'Site')
    Site.objects.all().delete()

    # Register SITE_ID = 1
    Site.objects.create(domain='example.com', name='ProjMan')

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(setup_site)
    ]
