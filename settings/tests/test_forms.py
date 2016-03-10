# -*- coding: utf-8 -*-
import allauth.account
from crispy_forms.helper import FormHelper
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
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

    def test_can_change_inlist_delete_confirm(self):
        user = User.objects.create_user('alice', 'alice@test.org', 'alice')
        self.assertEqual(user.settings.inlist_delete_confirm, True)
        form = forms.SettingsForm(data={'inlist_delete_confirm': False,
            'language': 'nl'})
        form.instance = user.settings

        form.is_valid()
        form.save()

        self.assertFalse(user.settings.inlist_delete_confirm)

    def test_inlist_delete_confirm_has_a_sensible_label(self):
        form = forms.SettingsForm()
        self.assertEqual(form.fields['inlist_delete_confirm'].label,
            forms.INLIST_DELETE_CONFIRM_LABEL)

    def test_can_change_action_delete_confirm(self):
        user = User.objects.create_user('alice', 'alice@test.org', 'alice')
        self.assertEqual(user.settings.action_delete_confirm, True)
        form = forms.SettingsForm(data={'action_delete_confirm': False,
            'language': 'nl'})
        form.instance = user.settings

        form.save()
        self.assertFalse(user.settings.action_delete_confirm)

    def test_action_delete_confirm_has_sensible_label(self):
        form = forms.SettingsForm()
        self.assertEqual(form.fields['action_delete_confirm'].label,
            forms.ACTION_DELETE_CONFIRM_LABEL)


class ChangePasswordFormTests(TestCase):
    def test_form_is_allauth_change_password_form(self):
        form = forms.ChangePasswordForm()
        self.assertIsInstance(form, allauth.account.forms.ChangePasswordForm)

    def test_form_uses_allauth_change_password_view(self):
        form = forms.ChangePasswordForm()
        self.assertEqual(form.helper.form_action,
            reverse('settings:change_password'))
