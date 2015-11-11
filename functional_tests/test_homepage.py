# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from selenium.webdriver.common.keys import Keys
import re

from . import remote
from .base import FunctionalTestCase
from .pages import accounts, landingpage, thirdparty

User = get_user_model()

class HomePageTest(FunctionalTestCase):
    def test_landingpage_shows_sitename_as_branding(self):
        """Branding should be dynamic and set to the sitename"""
        # Get the name of the site
        if self.against_staging:
            site_name = remote.get_sitename(self.server_host)
        else:
            site_name = get_current_site(None).name

        # Alice goes to the website
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)

        # The title says the name of the site
        self.assertIn(site_name, self.browser.title)

        # The branding on the header also has the name of the site
        self.assertEqual(site_name, page.branding.text)

    def test_can_login_from_landingpage(self):
        """Login from landing page using buildin method should be possible"""
        # Create a user account for Alice
        if self.against_staging:
            remote.create_user(self.server_host, 'alice', 'alice@test.com',
                'alice')
        else:
            User.objects.create_user('alice', 'alice@test.com', 'alice')

        # Alice goes to the website
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)

        # There is a header with the site's name in it, the name links
        # to the homepage (testing the value is done in
        # test_landingpage_shows_sitename_as_branding() now)
        self.assertTrue(page.branding.get_attribute('href').endswith('/en/'))
        # There is also a sign in button on the header
        self.assertEqual('sign in', page.header_signin.text.lower())

        # In the main body of the site there is also a sign in button
        self.assertEqual('sign in', page.body_signin.text.lower())

        # She clicks one of the sign in buttons and is send to the login page
        page.header_signin.click()
        self.assertIn('accounts/login/', self.browser.current_url)
        loginpage = accounts.LoginPage(self.browser)

        # Alice logs in using her account
        loginpage.username.send_keys('alice')
        loginpage.password.send_keys('alice')
        loginpage.password.send_keys(Keys.RETURN)

        # She ends up on a success page
        self.assertIn('accounts/profile/', self.browser.current_url)

    def test_can_login_using_persona_from_landingpage(self):
        """Test if we can login using persona"""
        # Alice goes to the website
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)

        # She clicks on a Sign in button
        page.header_signin.click()

        # She clicks on the Persona login link
        loginpage = accounts.LoginPage(self.browser)
        loginpage.persona.click()

        self.switch_to_new_window('Mozilla Persona')

        # She enters her email into the persona field
        persona = thirdparty.Persona(self.browser)
        persona.email.send_keys('alice@mockmyid.com')
        persona.email.send_keys(Keys.RETURN)

        # She sees that she is logged in
        self.switch_to_new_window('Sign In')
        self.wait_for(lambda: self.assertIn('accounts/profile/',
            self.browser.current_url), timeout=30)

    def test_register_with_django_auth_workflow(self):
        """Test if a user can register using the auth model from django"""
        # Alice goes to the website
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)

        # She clicks on a Sign in button
        page.header_signin.click()

        # Alice doesn't have a (social media) account, so she clicks
        # the register button
        loginpage = accounts.LoginPage(self.browser)
        loginpage.register.click()

        # Alice fills out the form, but doesn't fill in an email
        # so she doesn't get registered
        registerpage = accounts.RegisterPage(self.browser)
        registerpage.username.send_keys('alice')
        registerpage.password1.send_keys('alice-password')
        registerpage.password2.send_keys('alice-password')
        registerpage.username.send_keys(Keys.RETURN)

        self.assertEqual(len(registerpage.errors), 1)
        self.assertIn('This field is required', registerpage.errors[0].text)

        # Alice fills out the form again, this time including her email
        registerpage.password1.send_keys('alice-password')
        registerpage.password2.send_keys('alice-password')
        registerpage.email.send_keys('alice@test.com')
        registerpage.signup.click()

        # Alice is now logged in, but she goes to confirm her email anyway
        self.assertIn('accounts/profile', self.browser.current_url)
        # Alice finds an email in her inbox
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['alice@test.com'])

        # She finds a link in the email and clicks it
        urls = re.findall('http[s]?://\S+', email.body)
        self.browser.get(urls[0])

        # She lands on a page that lists here email address and has a
        # confirm button
        confirmpage = accounts.ConfirmEmailPage(self.browser)
        self.assertIn('alice@test.com', confirmpage.body.text)
        self.assertIn('confirm', confirmpage.confirm.text.lower())
        confirmpage.confirm.click()

        # She new ends up at the profile page
        self.assertIn('accounts/profile', self.browser.current_url)

    def test_reset_password_workflow(self):
        """Test whether a user can reset their password."""
        # Create an account for Alice
        User.objects.create_user('alice', 'alice@test.com', 'alice')

        # Alice goes to the login page
        self.browser.get(self.server_url)
        page = landingpage.LandingPage(self.browser)
        page.body_signin.click()

        # Alice has forgotten her password so on the login page she
        # clicks the reset password button
        loginpage = accounts.LoginPage(self.browser)
        loginpage.forgot.click()

        # On the login page she finds a password field which she fills in
        # and then she clicks the reset password button
        resetpage = accounts.PasswordResetPage(self.browser)
        resetpage.email.send_keys('alice@test.com')
        resetpage.reset.click()

        # Alice is redirected to a page which says she has been send an email
        resetdonepage = accounts.PasswordResetDonePage(self.browser)
        self.assertIn('We have sent you an e-mail', resetdonepage.body.text)

        # Alice has received an email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.to, ['alice@test.com'])

        # She finds a link in the email and clicks it
        urls = re.findall('http[s]?://\S+', email.body)
        self.browser.get(urls[0])

        # On the page she fills out the reset password form
        resetpage = accounts.ResetPasswordKeyPage(self.browser)
        resetpage.password1.send_keys('newpass')
        resetpage.password2.send_keys('newpass')
        resetpage.submit.click()

        # She ends up on a page saying that her password has been reset
        # and she decides to click a link to sign in
        resetdonepage = accounts.ResetPasswordKeyDonePage(self.browser)
        resetdonepage.signin.click()

        # She lands up on the login page where she can login
        loginpage = accounts.LoginPage(self.browser)
        loginpage.username.send_keys('alice')
        loginpage.password.send_keys('newpass')
        loginpage.signin.click()

        # She is now logged in
        self.assertIn('accounts/profile', self.browser.current_url)
