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

        # A generic style css is loaded
        links = self.browser.find_elements_by_tag_name('link')
        self.assertTrue(any(['css/style.css' in link.get_attribute('href')
            for link in links]))

        # She also sees that the MUI javascript is loaded
        scripts = self.browser.find_elements_by_tag_name('script')
        self.assertTrue(any(['mui.min.js' in s.get_attribute('src')
            for s in scripts]))

        # She also sees that jQuery is loaded
        self.assertTrue(any(['jquery-2.1.4.min.js' in s.get_attribute('src')
            for s in scripts]))

class AccountPagesLayout(FunctionalTestCase):
    """Smoke tests for the layout of pages under /account/"""
    def setUp(self):
        super(AccountPagesLayout, self).setUp()
        self.width = 1200
        self.browser.set_window_size(self.width, 800)

    def element_centered(self, e):
        """Tests if an element is centered"""
        return self.assertAlmostEqual(e.location['x'] + e.size['width'] / 2,
                self.width / 2, delta=5)

    def test_accounts_login_page(self):
        """Test the page under /accounts/login/"""
        # Alice goes to the login page directly
        self.browser.get(self.live_server_url + '/en/accounts/login/')

        # She sees that the username and password field are nicely centered
        username = self.browser.find_element_by_name('login')
        password = self.browser.find_element_by_name('password')
        self.element_centered(username)
        self.element_centered(password)
        # She sees that the remember me checkbox and the sign in button
        # are next to each other and on opposite sides
        remember = self.browser.find_element_by_name('remember')
        buttons = self.browser.find_elements_by_tag_name('button')
        signin = self.assertElementPresent(buttons, 'sign in')
        self.assertLess(remember.location['x'], self.width / 2)
        self.assertGreater(signin.location['x'], self.width / 2)
        self.assertAlmostEqual(remember.location['y'], signin.location['y'],
            delta=10)

    def test_accounts_signup_page(self):
        """Test the page under /accounts/signup/"""
        # Alice goes to the register page directly
        self.browser.get(self.live_server_url + '/en/accounts/signup/')

        # She sees that all the fields are nicely centered
        username = self.browser.find_element_by_name('username')
        password1 = self.browser.find_element_by_name('password1')
        password2 = self.browser.find_element_by_name('password2')
        email = self.browser.find_element_by_name('email')
        signup = self.browser.find_element_by_tag_name('button')

        self.element_centered(username)
        self.element_centered(password1)
        self.element_centered(password2)
        self.element_centered(email)
        # The sign up button should be aligned to the right
        self.assertGreater(signup.location['x'], self.width / 2)

    def test_accounts_password_reset_page(self):
        """Test the page under /accounts/password/reset/"""
        # Alice goes to the reset password page
        self.browser.get(self.live_server_url+'/en/accounts/password/reset/')

        # She sees that the email field is centered
        email = self.browser.find_element_by_name('email')
        self.element_centered(email)

        # She sees that the reset button is left aligned
        reset = self.browser.find_element_by_tag_name('button')
        self.assertLess(reset.location['x'], self.width / 2)
