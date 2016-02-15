# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from selenium.common.exceptions import NoSuchElementException
import math

from . import remote
from .base import FunctionalTestCase
from . import pages

User = get_user_model()

class CommonTest(FunctionalTestCase):
    def test_framework_is_loaded(self):
        # Alice visits the website
        self.browser.get(self.server_url)
        page = pages.landingpage.LandingPage(self.browser)

        # She sees that MUI css is loaded
        self.assertTrue(any(['mui.min.css' in s.get_attribute('href')
            for s in page.stylesheets]))

        # She sees that Font Awesome is loaded
        self.assertTrue(any(['font-awesome.min.css' in s.get_attribute('href')
            for s in page.stylesheets]))

        # A generic style css is loaded
        self.assertTrue(any(['css/style.css' in s.get_attribute('href')
            for s in page.stylesheets]))

        # She also sees that the MUI javascript is loaded
        self.assertTrue(any(['mui.min.js' in s.get_attribute('src')
            for s in page.scripts]))

        # She also sees that jQuery is loaded
        self.assertTrue(any(['jquery-2.1.4.min.js' in s.get_attribute('src')
            for s in page.scripts]))

    def test_settings_and_logout_are_in_dropdown_menu(self):
        # Alice logs in to the website
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)

        # There are no visible settings and logout links
        self.assertFalse(page.settings_link.is_displayed())
        self.assertFalse(page.logout.is_displayed())

        # She sees an icon on the top right corner, she clicks it and sees
        # the logout and settings links
        page.menu.click()
        self.assertTrue(page.settings_link.is_displayed())
        self.assertTrue(page.logout.is_displayed())

class AccountPagesLayout(FunctionalTestCase):
    """Smoke tests for the layout of pages under /account/"""
    def set_size(self):
        self.width = 1200
        self.browser.set_window_size(self.width, 800)

    def element_centered(self, e):
        """Tests if an element is centered"""
        return self.assertAlmostEqual(e.location['x'] + e.size['width'] / 2,
                self.width / 2, delta=5)

    def test_accounts_login_page(self):
        """Test the page under /accounts/login/"""
        # Alice goes to the login page directly
        self.browser.get(self.server_url + '/en/accounts/login/')
        self.set_size()
        page = pages.accounts.LoginPage(self.browser)

        # She sees that the username and password field are nicely centered
        self.element_centered(page.username)
        self.element_centered(page.password)

        # She sees that the sign in button and register button are on the
        # left side of the page, and that the forgot password is on the
        # right and vertically aligned with the sign in button
        self.assertLess(page.remember.location['x'], self.width / 2)
        self.assertLess(page.signin.location['x'], self.width / 2)
        self.assertLess(page.register.location['x'], self.width / 2)
        self.assertGreater(page.forgot.location['x'], self.width / 2)
        self.assertAlmostEqual(page.signin.location['y'],
            page.forgot.location['y'], delta=10)

    def test_accounts_signup_page(self):
        """Test the page under /accounts/signup/"""
        # Alice goes to the register page directly
        self.browser.get(self.server_url + '/en/accounts/signup/')
        self.set_size()
        page = pages.accounts.RegisterPage(self.browser)

        # She sees that all the fields are nicely centered
        self.element_centered(page.username)
        self.element_centered(page.password1)
        self.element_centered(page.password2)
        self.element_centered(page.email)
        # The sign up button should be aligned to the right
        self.assertGreater(page.signup.location['x'], self.width / 2)

    def test_accounts_password_reset_page(self):
        """Test the page under /accounts/password/reset/"""
        # Alice goes to the reset password page
        self.browser.get(self.server_url+'/en/accounts/password/reset/')
        self.set_size()
        page = pages.accounts.PasswordResetPage(self.browser)

        # She sees that the email field is centered
        self.element_centered(page.email)

        # She sees that the reset button is left aligned
        self.assertLess(page.reset.location['x'], self.width / 2)

    def test_accounts_logout_page(self):
        """Test the page under /accounts/logout/"""
        # Alice is a logged in user who goes to log out
        if self.against_staging:
            remote.create_user(self.server_host, 'alice', 'alice@test.com',
                 'alice')
        else:
            User.objects.create_user('alice', 'alice@test.com', 'alice')
        self.browser.get(self.server_url + '/en/accounts/login/')
        loginpage = pages.accounts.LoginPage(self.browser)
        loginpage.username.send_keys('alice')
        loginpage.password.send_keys('alice')
        loginpage.signin.click()

        self.browser.get(self.server_url + '/en/accounts/logout')
        self.set_size()

        # The sign out button is left aligned
        logoutpage = pages.accounts.LogoutPage(self.browser)
        self.assertLess(logoutpage.signout.location['x'], self.width / 2)
        self.assertGreater(logoutpage.signout.location['x'], self.width / 4)


class ProjectsPagesTests(FunctionalTestCase):
    """Smoke tests for the pages under /projects/"""
    def set_size(self):
        self.width = 1200
        self.browser.set_window_size(self.width, 800)

    def test_inlist_page(self):
        """Test the page under /projects/inlist/"""
        # Alice is a user who goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('This is a test item\n')

        # The text field and button to add items are horizontally aligned
        self.assertAlmostEqual(inlist_page.add_box.location['y'],
            inlist_page.add_button.location['y'],
            delta=math.ceil(inlist_page.add_button.size['height'] / 2))

        # The inlist is underneath the form
        self.assertLess(inlist_page.add_box.location['y'],
            inlist_page.thelist[0].location['y'])

    def test_actionlist_page(self):
        """Test the page under /projects/actions/"""
        # Alice is a user who goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She adds an item
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Complete this test\n')

        # The text field and button to add items are horizontally aligned
        self.assertAlmostEqual(action_page.add_box.location['y'],
            action_page.add_button.location['y'],
            delta=math.ceil(action_page.add_button.size['height'] / 2))

        # The action list is underneath the form
        self.assertLess(action_page.add_box.location['y'],
            action_page.thelist[0].location['y'])

    def test_create_project_page(self):
        """Test the page under /projects/project/create/"""
        # Alice is a user who goes to the create project page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        self.set_size()

        # The name and description fields are above each other and the
        # create button is at the bottom, aligned left
        create_page = pages.projects.CreateProjectPage(self.browser)
        self.assertLess(create_page.name_box.location['y'],
            create_page.description_box.location['y'])
        self.assertLess(create_page.description_box.location['y'],
            create_page.create_button.location['y'])
        self.assertLess(create_page.description_box.location['x'],
            self.width / 2)

    def test_project_page(self):
        """Test the page under /projects/project/PK/"""
        # Alice is a user who has a project
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            remote.create_project(self.server_host, 'alice', 'Test layout',
                'Also test styling')
        else:
            from projects.factories import ProjectFactory
            ProjectFactory(user=user, name='Test layout',
                description='Also test styling')
        self.browser.refresh()
        self.create_action('alice', 'Test the title layout', 'Test layout')
        self.create_action('alice', 'Test the action layout', 'Test layout')

        # She goes to the project page
        page = pages.projects.BaseProjectPage(self.browser)
        page.project_link('Test layout').click()
        project_page = pages.projects.ProjectPage(self.browser)

        # The title is on the top, with the project edit and delete buttons to
        # the right of the title, but not next to it (they are in the right
        # half of the page while the title is on the left)
        self.set_size()
        self.assertLess(project_page.title.location['x'], self.width / 2)
        self.assertGreater(project_page.edit.location['x'], self.width / 2)
        self.assertGreater(project_page.delete.location['x'], self.width / 2)
        self.assertAlmostEqual(project_page.title.location['y'],
            project_page.edit.location['y'], delta=10)
        self.assertAlmostEqual(project_page.title.location['y'],
            project_page.delete.location['y'], delta=10)

        # The add action form is under that, the text box is on the left
        # while the button is on the right
        self.assertLess(project_page.info.location['y'],
            project_page.add_box.location['y'])
        self.assertLess(project_page.add_box.location['x'], self.width / 2)
        self.assertGreater(project_page.add_button.location['x'], self.width/2)
        self.assertAlmostEqual(project_page.add_box.location['y'],
            project_page.add_button.location['y'],
            delta=math.ceil(project_page.add_button.size['height'] / 2))
        self.assertEqual(project_page.add_button.location['x'],
            project_page.edit.location['x'])

        # The action list is under that, with the manipulation buttons
        # on the right half of the page as well
        action = project_page.get_list_rows(project_page.thelist)[0]
        self.assertLess(project_page.add_box.location['y'],
            action['text'].location['y'])
        self.assertLess(action['text'].location['x'], self.width / 2)
        self.assertGreater(action['delete'].location['x'], self.width / 2)
        self.assertGreater(action['move'].location['x'], self.width / 2)
        self.assertAlmostEqual(action['text'].location['y'],
            action['delete'].location['y'], delta=10)
        self.assertAlmostEqual(action['text'].location['y'],
            action['move'].location['y'], delta=10)

    def test_action_edit_page(self):
        """Test the page under /projects/actions/PK/move/"""
        # Alice is a user who has an action
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        self.create_action('alice', 'Test some more layouts')

        # She goes to the action's move page
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        action = action_page.get_list_rows(action_page.thelist)[0]
        action['edit'].click()

        # She sees that the ordering of the elements is text, project,
        # dealine, submit button
        edit_page = pages.projects.EditActionPage(self.browser)
        self.assertLess(edit_page.text_box.location['y'],
            edit_page._select.location['y'])
        self.assertLess(edit_page._select.location['y'],
            edit_page.deadline_date.location['y'])
        self.assertLess(edit_page.deadline_date.location['y'],
            edit_page.confirm.location['y'])

        # She also sees that the label for the select element is visible
        # (this is here because we used to check for the label not being
        # present)
        select_label = self.browser.find_element_by_xpath(
            "//label[@for='id_project']")
