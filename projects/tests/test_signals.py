# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.test import TestCase

from projects import models

User = get_user_model()

class ActionlistProjectTests(TestCase):
    def test_create_action_project_on_user_creation(self):
        user = User.objects.create(username='alice', password='alice')
        ps = models.Project.objects.filter(user=user)

        self.assertEqual(ps.count(), 1)
        self.assertEqual(ps[0].name, 'Actions')
