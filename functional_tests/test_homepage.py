# -*- coding: utf-8 -*-

from .base import FunctionalTestCase

class HomePageTest(FunctionalTestCase):
    def test_temp_homepage_test(self):
        """Test if Django is set up, can be removed later on."""
        # Alice goes to the website
        self.browser.get('http://localhost:8000')

        # The default first time setup page is loaded
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('It worked!', body.text)
