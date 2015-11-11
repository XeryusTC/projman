# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.sites.shortcuts import get_current_site

class Command(BaseCommand):
    def handle(self, *args, **options):
        site = get_current_site(None)
        self.stdout.write(site.name)
