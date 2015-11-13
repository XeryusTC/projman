# -*- coding: utf-8 -*-
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
import unittest

from project import views

class TestMainPage(TestCase):
    def test_mainpage_url_resolves_to_mainpage_view(self):
        found = resolve(reverse('project:main'))
        self.assertEqual(found.func.__name__,
            views.MainPageView.as_view().__name__)

    def test_mainpage_uses_correct_templates(self):
        response = self.client.get('/en/project/')
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'project/base.html')
        self.assertTemplateUsed(response, 'project/mainpage.html')
