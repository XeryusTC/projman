# -*- coding: utf-8 -*-
from .base import FunctionalTestCase
from . import pages

class SettingsTests(FunctionalTestCase):
    def test_language_setting(self):
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # On the top of the page she sees a button, she decides to click it
        page = pages.projects.BaseProjectPage(self.browser)
        page.settings_link.click()

        # She is directed to a new page, which has a language option
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertIn('Language', settings_page.settings_list)
        self.assertNotIn('Taal', settings_page.settings_list)
        # Alice changes the language to Dutch
        settings_page.language.select_by_value('nl')

        # She also submits the form
        settings_page.confirm.click()

        # She sees that the page is now in Dutch
        self.assertNotIn('Language', settings_page.settings_list)
        self.assertIn('Taal', settings_page.settings_list)
