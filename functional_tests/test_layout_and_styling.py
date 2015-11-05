# -*- coding: utf-8 -*-

from .base import FunctionalTestCase

class StylesheetTest(FunctionalTestCase):
    def test_framework_is_loaded(self):
        # Alice visits the website
        self.browser.get(self.live_server_url)

        # She sees that MUI css is loaded
        links = self.browser.find_elements_by_tag_name('link')
        self.assertTrue(any(['mui.min.css' in link.get_attribute('href')
            for link in links]))

        # She also sees that the MUI javascript is loaded
        scripts = self.browser.find_elements_by_tag_name('script')
        self.assertTrue(any(['mui.min.js' in s.get_attribute('src')
            for s in scripts]))
