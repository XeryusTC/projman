# -*- coding: utf-8 -*-

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver

DEFAULT_WAIT = 5

class FunctionalTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        for handle in self.browser.window_handles:
            self.browser.switch_to_window(handle)
            self.browser.close()

    def assertElementPresent(self, elements, text):
        for e in elements:
            if text.lower() == e.text.lower():
                return e
        else:
            self.fail("'{}' not in elements.text".format(text))
