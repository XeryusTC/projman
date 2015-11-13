# -*- coding: utf-8 -*-

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import time
import sys

from . import remote

DEFAULT_WAIT = 5

class FunctionalTestCase(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        for arg in sys.argv:
            if 'liveserver' in arg: # pragma: no cover
                cls.server_host = arg.split('=')[1]
                cls.server_url = 'http://' + cls.server_host
                cls.against_staging = True
                return # Skip setting up a local test server
        # Local FT, start a local server
        super(FunctionalTestCase, cls).setUpClass()
        cls.server_url = cls.live_server_url
        cls.against_staging = False

    @classmethod
    def tearDownClass(cls):
        if not cls.against_staging:
            super(FunctionalTestCase, cls).tearDownClass()

    def setUp(self):
        if self.against_staging:
            remote.reset_database(self.server_host)
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

    def is_logged_in(self):
        self.assertIn('accounts/profile/', self.browser.current_url)
