# -*- coding: utf-8 -*-

from .base import FunctionalTestCase

class HomePageTest(FunctionalTestCase):
    def test_landingpage_test(self):
        """Test if we arrive on the landing page"""
        # Alice goes to the website
        self.browser.get(self.live_server_url)

        # The title says the name of the site
        self.assertIn('ProjMan', self.browser.title)

        # There is a header with the site's name in it
        header = self.browser.find_element_by_id('header')
        self.assertIn('ProjMan', header.text)
        # There is also a sign in button on the header
        self.assertIn('Sign in', header.text)

        # In the main body of the site there is also a sign in button
        content = self.browser.find_element_by_id('content')
        self.assertIn('Sign in', content.text)
