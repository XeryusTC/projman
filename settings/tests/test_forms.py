# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from django.contrib.auth import get_user_model
from django.test import TestCase

from settings import forms

User = get_user_model()

class SettingsFormTests(TestCase):
    def test_form_crispy_helper(self):
        form = forms.SettingsForm()
        self.assertIsInstance(form.helper, FormHelper)
        self.assertEqual(form.helper.form_method.lower(), 'post')

    def test_can_change_user_language(self):
        user = User.objects.create_user('alice', 'alice@test.org', 'alice')
        self.assertEqual(user.settings.language, 'en-us')
        form = forms.SettingsForm(data={'language': 'nl'})
        form.instance = user.settings

        form.is_valid()
        form.save()

        self.assertEqual(user.settings.language, 'nl')
