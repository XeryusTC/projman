# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model

from . import remote
from .base import FunctionalTestCase
from .pages import accounts, landingpage

User = get_user_model()

class StylesheetTest(FunctionalTestCase):
    def test_framework_is_loaded(self):
        # Alice visits the website
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)

        # She sees that MUI css is loaded
        self.assertTrue(any(['mui.min.css' in s.get_attribute('href')
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
        page = accounts.LoginPage(self.browser)

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
        page = accounts.RegisterPage(self.browser)

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
        page = accounts.PasswordResetPage(self.browser)

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
        loginpage = accounts.LoginPage(self.browser)
        loginpage.username.send_keys('alice')
        loginpage.password.send_keys('alice')
        loginpage.signin.click()

        self.browser.get(self.server_url + '/en/accounts/logout')
        self.set_size()

        # The sign out button is left aligned
        logoutpage = accounts.LogoutPage(self.browser)
        self.assertLess(logoutpage.signout.location['x'], self.width / 2)
        self.assertGreater(logoutpage.signout.location['x'], self.width / 4)
