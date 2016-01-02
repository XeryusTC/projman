# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from projects.models import ActionlistItem, Project

User = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('user')
        parser.add_argument('text', nargs='+')
        parser.add_argument('--project', nargs='*', default='')

    def handle(self, *args, **options):
        text = ' '.join(options['text'])
        u = User.objects.get(username=options['user'])

        p = None
        if options['project'] != '':
            project = ' '.join(options['project'])
            p = Project.objects.get(user=u, name=project)

        a = ActionlistItem.objects.create(user=u, text=text, project=p)
        a.full_clean() # Needed to not create duplicate items
        a.save()
        self.stdout.write(str(a.pk))
