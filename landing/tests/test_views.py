# -*- coding: utf-8 -*-
from django.contrib.sites.models import Site
from django.core.urlresolvers import resolve
from django.test import TestCase

from landing.views import LandingView

class LandingPageTests(TestCase):
    def test_root_url_resolves_to_landing_page_view(self):
        found = resolve('/en/')
        self.assertEqual(found.func.__name__, LandingView.as_view().__name__)

    def test_landing_page_uses_correct_templates(self):
        response = self.client.get('/en/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'landing/index.html')

    def test_site_context_variable_set(self):
        response = self.client.get('/en/')
        self.assertIsInstance(response.context['site'], Site)
