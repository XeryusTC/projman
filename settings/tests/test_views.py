# -*- coding: utf-8 -*-
import allauth.account.forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
from django.utils import translation
from unittest.mock import patch

from common.tests import ViewTestMixin, RequestFunctionMixin
from settings import forms
from settings import views
from settings.tests.test_models import reset_user_settings

User = get_user_model()
alice = None

def setUpModule():
    global alice
    alice = User.objects.create_user('alice', 'alice@test.org', 'alice')

def tearDownModule():
    alice.delete()

class SettingsViewTest(ViewTestMixin, TestCase):
    templates = ('base_with_sidebar.html', 'settings/base.html',
        'settings/main.html')
    explicit_url = '/en/settings/'

    def setUp(self):
        reset_user_settings(alice.settings)
        translation.activate(alice.settings.language)

        self.url = reverse('settings:main')
        self.view = views.SettingsMainView.as_view()

    def tearDown(self):
        translation.deactivate()

    def test_uses_settings_form(self):
        response = self.get_request(alice)
        self.assertIsInstance(response.context_data['form'],
            forms.SettingsForm)

    def test_POST_redirects_to_main_settings_view(self):
        response = self.post_request(alice, {'language': 'en'})
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.url, r'/en(-us)?/settings/')

    def test_POST_request_can_change_users_language_setting(self):
        self.assertEqual(alice.settings.language, 'en-us')
        self.post_request(alice, {'language': 'nl'})
        self.assertEqual(alice.settings.language, 'nl')

    def test_form_instance_user_is_requesting_user(self):
        response = self.get_request(alice)
        self.assertEqual(response.context_data['form'].instance.user, alice)

    @patch('settings.views.translation.activate')
    def test_POST_request_activates_appropriate_language(self, mock_activate):
        self.post_request(alice, {'language': 'nl'})
        mock_activate.assert_called_once_with('nl')

    def test_POST_request_can_change_users_inlist_delete_confirm_setting(self):
        self.assertTrue(alice.settings.inlist_delete_confirm)
        self.post_request(alice, {'language': 'en'})
        self.assertFalse(alice.settings.inlist_delete_confirm)

    def test_POST_request_can_change_users_inlist_delete_confirm_setting2(self):
        alice.settings.inlist_delete_confirm = False
        self.post_request(alice, {'language': 'en',
            'inlist_delete_confirm': True})
        self.assertTrue(alice.settings.inlist_delete_confirm)

    def test_POST_request_can_change_users_action_delete_confirm_setting(self):
        self.assertTrue(alice.settings.action_delete_confirm)
        self.post_request(alice, {'language': 'en'})
        self.assertFalse(alice.settings.action_delete_confirm)

    def test_POST_request_can_change_users_action_delete_confirm_setting2(self):
        alice.settings.action_delete_confirm = False
        self.post_request(alice, {'language': 'en',
            'action_delete_confirm': True})
        self.assertTrue(alice.settings.action_delete_confirm)


class SetLanguageViewTests(RequestFunctionMixin, TestCase):
    def setUp(self):
        self.url = reverse('settings:set_language')
        self.view = views.SetLanguageView.as_view()

    def test_set_language_url_resolves_to_set_language_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_redirects_to_projects_main_view(self):
        response = self.get_request(alice)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:main'))

    @patch('settings.views.translation.activate')
    def test_changes_active_language(self, mock_activate):
        alice.settings.language = 'nl'
        self.get_request(alice)
        mock_activate.assert_called_once_with('nl')

    def test_sets_language_in_session(self):
        alice.settings.language = 'nl'
        request = self.factory.get(self.url)
        request.user = alice
        request.session = {}

        self.view(request, self.url)

        self.assertEqual(request.session[translation.LANGUAGE_SESSION_KEY],
            alice.settings.language)

    @patch('settings.views.translation.activate')
    def test_can_deal_with_overly_specific_languages(self, mock_activate):
        """
        Language codes like en-us should be converted to more generic ones
        when they are not directly supported
        """
        alice.settings.language = 'nl-su' # Overly specific (for now)

        request = self.get_request(alice)

        mock_activate.assert_called_once_with('nl')

    def test_view_is_used_when_user_logs_in(self):
        self.assertEqual(settings.LOGIN_REDIRECT_URL, "settings:set_language")


class AccountSettingsViewTests(ViewTestMixin, TestCase):
    templates = ('base_with_sidebar.html', 'settings/base.html',
        'settings/account.html')
    explicit_url = '/en/settings/account/'

    def setUp(self):
        self.url = reverse('settings:account')
        self.view = views.AccountSettingsView.as_view()

    def test_has_change_password_form_in_context(self):
        response = self.get_request(alice)
        self.assertIsNotNone(response.context_data['password_form'])
        self.assertIsInstance(response.context_data['password_form'],
            forms.ChangePasswordForm)


class ChangePasswordViewTests(RequestFunctionMixin, TestCase):
    def setUp(self):
        self.url = reverse('settings:change_password')
        self.view = views.ChangePasswordView.as_view()

    def test_success_url_is_set_to_account_settings(self):
        self.assertEqual(views.ChangePasswordView().success_url,
            reverse('settings:account'))

    def test_is_allauth_change_password_view(self):
        self.assertIsInstance(views.ChangePasswordView(),
            allauth.account.views.PasswordChangeView)
