# -*- coding: utf-8 -*-
from selenium import webdriver
import unittest

from .base import FunctionalTestCase
from . import pages
from . import remote
import projects.factories

class SettingsTests(FunctionalTestCase):
    def test_can_navigate_to_projects_from_settings(self):
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She clicks on the settings link
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
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
        page.menu.click()
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
        self.assertIn('/nl/', self.browser.current_url)
        self.assertNotIn('/en/', self.browser.current_url)

    def test_language_setting_is_remembered_across_pages_and_sessions(self):
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She goes to the settings
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
        project_page.settings_link.click()

        # Her language is currently set to English, but she wants it in Dutch
        self.assertIn('/en/', self.browser.current_url)
        self.assertNotIn('/nl/', self.browser.current_url)
        settings_page = pages.settings.SettingsPage(self.browser)
        settings_page.language.select_by_value('nl')
        settings_page.confirm.click()

        # When she goes back to the projects she sees that key elements
        # have been translated
        settings_page.return_link.click()
        project_page.menu.click()
        self.assertEqual(project_page.logout.text.lower(), 'afmelden')
        self.assertEqual(project_page.settings_link.text.lower(),
            'instellingen')
        self.assertEqual('in lijst',
            project_page.inlist_link(project_page.sidebar).text.lower())

        # Alice leaves the website
        # When alice returns later she sees that everything is still in Dutch
        self.restart_browser()
        self.login_user('alice', 'alice')
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
        self.assertEqual(project_page.logout.text.lower(), 'afmelden')
        self.assertEqual(project_page.settings_link.text.lower(),
            'instellingen')
        self.assertEqual('in lijst',
            project_page.inlist_link(project_page.sidebar).text.lower())

    def test_inlist_delete_confirm(self):
        """Test if the inlist confirm delete setting skips the confirm page"""
        # Alice is a user who logs into the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She goes to the settings
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
        project_page.settings_link.click()

        # Currently the option to ask for confirmation when inlist items
        # are deleted is on
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertTrue(settings_page.inlist_delete_confirm.is_selected())

        # She switches it off and saves her settings
        settings_page.inlist_delete_confirm.click()
        settings_page.confirm.click()

        # Alice goes to add an item to her inlist
        settings_page.return_link.click()
        project_page.inlist_link(project_page.sidebar).click()
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys("Don't test the settings\n")

        # Deciding that this is a stupid idea she deletes the item
        self.assertIn("Don't test the settings",
            [item.text for item in inlist_page.thelist])
        item = inlist_page.listrows[0]
        inlist_page.delete_item(item).click()

        # She sees that she is not send to the confirm page but instead
        # the item has just disapeared
        self.assertNotEqual(self.browser.title, 'Delete in list item')
        self.assertEqual(self.browser.title, 'In list')
        self.assertEqual(len(inlist_page.listrows), 0)

    def test_actionlist_delete_confirm(self):
        # Alice is a user who logs into the website
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She goes to the settings
        page = pages.projects.BaseProjectPage(self.browser)
        page.menu.click()
        page.settings_link.click()

        # She sees an option that asks for confirmation when an action
        # item gets deleted
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertTrue(settings_page.action_delete_confirm.is_selected())
        self.assertIn('Ask for confirmation when deleting actions',
            settings_page.content.text,)

        # She switches it off and saves her settings
        settings_page.action_delete_confirm.click()
        settings_page.confirm.click()

        # Alice goes to add an item to her actionlist
        settings_page.return_link.click()
        page.action_link(page.sidebar).click()
        actionlist_page = pages.projects.ActionlistPage(self.browser)
        actionlist_page.add_box.send_keys('Watch more series\n')

        # Alice deletes the item
        item = actionlist_page.get_list_rows(actionlist_page.thelist)[0]
        item['delete'].click()

        # The item gets deleted without going through the confirmation page
        self.assertNotEqual(self.browser.title, 'Delete action')
        self.assertEqual(self.browser.title, 'Actions')
        self.assertEqual(len(actionlist_page.thelist), 0)

        # She also has an action on a project
        if self.against_staging:
            remote.create_project(self.server_host, 'alice', 'Plan a rave', '')
            remote.create_action(self.server_host, 'alice', 'Find a location',
                'Plan a rave')
        else:
            p = projects.factories.ProjectFactory(user=user,
                name='Plan a rave')
            projects.factories.ActionlistItemFactory(user=user, project=p,
                text='Find a location')
        self.browser.refresh()

        # She goess to delete the action from the project
        page.project_link('Plan a rave').click()
        project_page = pages.projects.ProjectPage(self.browser)
        item = project_page.get_list_rows(project_page.thelist)[0]
        item['delete'].click()

        # This item also got deleted without needing confirmation
        self.assertNotEqual(self.browser.title, 'Delete action')
        self.assertEqual(self.browser.title, 'Plan a rave')
        self.assertEqual(len(project_page.thelist), 0)

    def test_settings_page_has_return_link_in_sidebar(self):
        # Alice is a user who goes to the settings
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
        project_page.settings_link.click()

        # There is a sidebar on the page
        settings_page = pages.settings.SettingsPage(self.browser)
        self.assertIsNotNone(settings_page.sidebar)

        # In the sidebar there is a button that returns to the projects page
        self.assertIn('Home', project_page.sidebar.text)
        # When she clicks it she is returned to the projects page
        settings_page.sidebar_return_link.click()
        project_page.inlist_link(project_page.sidebar).click()

    def test_can_change_password(self):
        # Alice is a user who goes to the settings
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.menu.click()
        project_page.settings_link.click()

        # She sees an account link in the sidebar and clicks it
        settings_page = pages.settings.SettingsPage(self.browser)
        settings_page.account_link.click()

        # Here she sees a link that says she can change her password
        # she clicks it
        account_settings = pages.settings.AccountSettingsPage(self.browser)
        account_settings.change_password.click()

        # She ends up on a new page where the password can be changed
        change_page = pages.settings.ChangePasswordPage(self.browser)
        change_page.old_password.send_keys('alice')
        change_page.password1.send_keys('security')
        change_page.password2.send_keys('security')
        change_page.confirm.click()

        # Alice then signs out
        settings_page.menu.click()
        settings_page.logout.click()

        # She must now log in with her new password
        self.fail('Finish test')
