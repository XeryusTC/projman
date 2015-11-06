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
        header = self.browser.find_element_by_tag_name('header')
        self.assertIn('ProjMan', header.text)
        # There is also a sign in button on the header
        buttons = header.find_elements_by_tag_name('button')
        b = self.assertElementPresent(buttons, 'sign in')

        # In the main body of the site there is also a sign in button
        content = self.browser.find_element_by_id('content')
        buttons = content.find_elements_by_tag_name('button')
        self.assertElementPresent(buttons, 'sign in')
