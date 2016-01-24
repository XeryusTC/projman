# -*- coding: utf-8 -*-
from django.core.urlresolvers import resolve, reverse

from common.tests import ViewTestCase
from settings import views

class SettingsViewTest(ViewTestCase):
    def setUp(self):
        self.url = reverse('settings:main')
        self.view = views.SettingsMainView.as_view()

    def test_settings_base_url_resolves_to_settings_main_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)
