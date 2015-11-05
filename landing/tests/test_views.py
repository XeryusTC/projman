from django.core.urlresolvers import resolve
from django.test import TestCase, RequestFactory
import unittest

from landing.views import LandingView

class LandingPageTests(TestCase):
    def test_root_url_resolves_to_landing_page_view(self):
        found = resolve('/')
        self.assertEqual(found.func.__name__, LandingView.as_view().__name__)

    def test_landing_page_uses_correct_templates(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'landing/index.html')
