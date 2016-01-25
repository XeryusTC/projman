# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase

from settings import models

User = get_user_model()

class SettingsTests(TestCase):
    def test_create_settings_on_user_creation(self):
        user = User.objects.create_user('alice', 'alice@test.org', 'alice')
        settings = models.Settings.objects.filter(user=user)

        self.assertEqual(settings.count(), 1)
