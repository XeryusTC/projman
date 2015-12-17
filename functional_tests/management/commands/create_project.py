# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import Project

User = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('user')
        parser.add_argument('name', nargs='+')
        parser.add_argument('--description', nargs='*', default='')

    def handle(self, *args, **options):
        name = ' '.join(options['name'])
        description = ' '.join(options['description'])
        u = User.objects.get(username=options['user'])
        p = Project.objects.create(user=u, name=name, description=description)
        p.save()
        self.stdout.write(str(p.pk))
