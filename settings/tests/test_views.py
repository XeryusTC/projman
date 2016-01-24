# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve, reverse

from common.tests import ViewTestCase
from settings import views

User = get_user_model()
alice = None

def setUpModule():
    global alice
    alice = User.objects.create_user('alice', 'alice@test.org', 'alice')

def tearDownModule():
    alice.delete()

class SettingsViewTest(ViewTestCase):
    def setUp(self):
        self.url = reverse('settings:main')
        self.view = views.SettingsMainView.as_view()

    def test_settings_base_url_resolves_to_settings_main_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_settings_main_view_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get('/en/settings/')
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'settings/base.html')
        self.assertTemplateUsed(response, 'settings/main.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.url,
            r'/en(-us)?/accounts/login/\?next=' + self.url)
