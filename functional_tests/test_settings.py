# -*- coding: utf-8 -*-
from selenium import webdriver
import unittest

from .base import FunctionalTestCase
from . import pages

class SettingsTests(FunctionalTestCase):
    def test_can_navigate_to_projects_from_settings(self):
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She clicks on the settings link
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.settings_link.click()

        # She ends up on the settings page
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertEqual('Settings', self.browser.title)

        # She wants to go back to the projects
        settings_page.return_link.click()

        # She ends up on the project_page
        project_page.inlist_link(project_page.sidebar).click()

    def test_language_setting(self):
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # On the top of the page she sees a button, she decides to click it
        page = pages.projects.BaseProjectPage(self.browser)
        page.settings_link.click()

        # She is directed to a new page
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertEqual('Settings', self.browser.title)

        # On the page there is a language setting
        self.assertIn('Language', settings_page.settings_list)
        self.assertNotIn('Taal', settings_page.settings_list)
        # Alice changes the language to Dutch
        settings_page.language.select_by_value('nl')

        # She also submits the form
        settings_page.confirm.click()

        # She sees that the page is now in Dutch
        self.assertNotIn('Language', settings_page.settings_list)
        self.assertIn('Taal', settings_page.settings_list)
        self.assertEqual('Instellingen', self.browser.title)
