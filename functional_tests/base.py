# -*- coding: utf-8 -*-

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time

DEFAULT_WAIT = 5

class FunctionalTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(DEFAULT_WAIT)

    def tearDown(self):
        self.browser.quit()

    def assertElementPresent(self, elements, text):
        for e in elements:
            if text.lower() == e.text.lower():
                return e
        else:
            self.fail("'{}' not in elements.text".format(text))

    def switch_to_new_window(self, text_in_title): # pragma: no cover
        retries = 100
        while retries > 0:
            for handle in self.browser.window_handles:
                self.browser.switch_to_window(handle)
                if text_in_title in self.browser.title:
                    return
            retries -= 1
            time.sleep(0.1)
        self.fail('Could not find window')

    def wait_for(self, func, timeout=DEFAULT_WAIT): # pragma: no cover
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                return func()
            except (AssertionError, WebDriverException):
                time.sleep(0.1)
        # One more try, which will raise any errors if outstanding
        return func()
