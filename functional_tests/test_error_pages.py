# -*- coding: utf-8 -*-
from .base import FunctionalTestCase

class ErrorPagesTests(FunctionalTestCase):
    def test_403_page(self):
        # Alice is a visitor who encounters a page she isn't supposed to visit
        self.browser.get(self.server_url + '/403/')
        # She sees a 403 error in the browser's title
        self.assertIn('403 Forbidden', self.browser.title)

        # She also sees the 403 error on the page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('403 Forbidden', body.text)

    def test_404_page(self):
        # Alice is a visitor who encounters a non-existing page
        self.browser.get(self.server_url + '/404/')
        # She sees a 404 error in the title
        self.assertIn('404 Not Found', self.browser.title)

        # She also sees the 404 error on the page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('404 Not Found', body.text)

    def test_500_page_setup(self):
        # Alice visits a page that breaks the server somehow
        self.browser.get(self.server_url + '/500/')
        # She sees a 500 error in the browser's title
        self.assertIn('500 Internal Server Error', self.browser.title)

        # She also sees the 500 error on the page
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('500 Internal Server Error', body.text)
