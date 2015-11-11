# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('username')
        parser.add_argument('password')
        parser.add_argument('email')

    def handle(self, *args, **options):
        u = User.objects.create_user(username=options['username'],
            email=options['email'], password=options['password'])
        u.save()
