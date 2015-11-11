# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models

def setup_site(apps, schema_editor):
    """Populate the sites model"""
    Site = apps.get_model('sites', 'Site')
    Site.objects.all().delete()

    # Register SITE_ID = 1
    try:
        domain = settings.DOMAIN
    except:
        domain = 'example.com'
    Site.objects.create(domain=domain, name='ProjMan')

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
            migrations.RunPython(setup_site)
    ]
