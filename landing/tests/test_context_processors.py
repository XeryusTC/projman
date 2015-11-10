# -*- coding: utf-8 -*-
from django.contrib.sites.shortcuts import get_current_site
from django.test import RequestFactory
import unittest

from landing import context_processors as cp

class TestSitesContextProcessor(unittest.TestCase):
    def test_site_is_set(self):
        request = RequestFactory().get('/en/')
        self.assertEqual(cp.site(request)['site'], get_current_site(request))
