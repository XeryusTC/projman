# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
import email
from imapclient import IMAPClient
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import re
import unittest

from . import remote
from .base import FunctionalTestCase
from .pages import accounts, landingpage, thirdparty, projects

User = get_user_model()

class HomePageTest(FunctionalTestCase):
    def get_email_from_web(self, host, account, password,
            ssl=True): # pragma: no cover
        conn = IMAPClient(host, use_uid=True, ssl=ssl)
        conn.login(account, password)
        self.assertTrue(conn.folder_exists('Inbox'))
        select_info = conn.select_folder('Inbox')

        messages = self.wait_for(lambda: self.has_unseen_emails(conn),
            timeout=15)
        response = conn.fetch(messages, ['RFC822'])
        for msgid, data in response.items():
            m = email.message_from_bytes(data[b'RFC822'])
            email_body = m.get_payload()
        return email_body

    def has_unseen_emails(self, mail): # pragma: no cover
        messages = mail.search(['UNSEEN'])
        self.assertGreater(len(messages), 0)
        return messages

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
        self.is_logged_in()

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
        if self.against_staging:
            registerpage.email.send_keys(settings.TEST_EMAIL_ACCOUNT)
        else:
            registerpage.email.send_keys('alice@test.com')
        registerpage.signup.click()

        # Alice is now logged in, but she goes to confirm her email anyway
        self.is_logged_in()

        # Alice finds an email in her inbox
        if self.against_staging:
            email_body = self.get_email_from_web(settings.TEST_EMAIL_HOST,
                settings.TEST_EMAIL_ACCOUNT, settings.TEST_EMAIL_PASSWORD)
        else:
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, ['alice@test.com'])
            email_body = email.body

        # She finds a link in the email and clicks it
        urls = re.findall('http[s]?://\S+', email_body)
        self.browser.get(urls[0])

        # She lands on a page that lists here email address and has a
        # confirm button
        confirmpage = accounts.ConfirmEmailPage(self.browser)
        if self.against_staging:
            self.assertIn(settings.TEST_EMAIL_ACCOUNT, confirmpage.body.text)
        else:
            self.assertIn('alice@test.com', confirmpage.body.text)
        self.assertIn('confirm', confirmpage.confirm.text.lower())
        confirmpage.confirm.click()

        # She is now properly logged in
        self.is_logged_in()

    def test_reset_password_workflow(self):
        """Test whether a user can reset their password."""
        # Create an account for Alice
        if self.against_staging:
            remote.create_user(self.server_host, 'alice',
                settings.TEST_EMAIL_ACCOUNT, 'alice')
        else:
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
        if self.against_staging:
            resetpage.email.send_keys(settings.TEST_EMAIL_ACCOUNT)
        else:
            resetpage.email.send_keys('alice@test.com')
        resetpage.reset.click()

        # Alice is redirected to a page which says she has been send an email
        resetdonepage = accounts.PasswordResetDonePage(self.browser)
        self.assertIn('We have sent you an e-mail', resetdonepage.body.text)

        # Alice has received an email
        if self.against_staging:
            email_body = self.get_email_from_web(settings.TEST_EMAIL_HOST,
                settings.TEST_EMAIL_ACCOUNT, settings.TEST_EMAIL_PASSWORD)
        else:
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertEqual(email.to, ['alice@test.com'])
            email_body = email.body

        # She finds a link in the email and clicks it
        urls = re.findall('http[s]?://\S+', email_body)
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
        self.is_logged_in()

    def test_can_log_out_after_log_in(self):
        import time
        # Alice is a returning user
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        # She clicks the log out button
        page = projects.BaseProjectPage(self.browser)
        page.logout.click()

        # She ends up on the confirmation page
        confirmpage = accounts.LogoutConfirmPage(self.browser)
        confirmpage.confirm.click()

        # She ends up on the landing page
        self.assertTrue(self.browser.current_url.endswith('/en/'))

    def test_logged_in_user_goes_to_main_page_when_requesting_landing(self):
        """When a user is already logged in and they visit the main URL
        they should be redirected to the LOGIN_REDIRECT_URL"""
        # Alice is a logged in user
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        # Alice visits the site again at a later date, but her session is
        # still stored so she is automatically logged in and redirected to
        # the main page
        self.browser.get(self.server_url)

        # She ended up at the main page (check directly instead of using a
        # helper like function is_logged_in because its internals might
        # change and make this test fail
        self.assertTrue(self.browser.current_url.endswith('/en/projects/'))
