# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core import mail
from selenium.webdriver.common.keys import Keys
import re

from .base import FunctionalTestCase
from .pages import accounts, landingpage, thirdparty

User = get_user_model()

class HomePageTest(FunctionalTestCase):
    def test_can_login_from_landingpage(self):
        """Login from landing page using buildin method should be possible"""
        # Create a user account for Alice
        User.objects.create_user('alice', 'alice@test.com', 'alice')

        # Alice goes to the website
        self.browser.get(self.live_server_url)
        page = landingpage.LandingPage(self.browser)

        # The title says the name of the site
        self.assertIn('ProjMan', self.browser.title)

        # There is a header with the site's name in it, the name links
        # to the homepage
        self.assertEqual('ProjMan', page.branding.text)
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
        self.browser.get(self.live_server_url)
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
        self.browser.get(self.live_server_url)
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
        self.assertIn('Confirm', confirmpage.confirm.text)
        confirmpage.confirm.click()

        # She new ends up at the profile page
        self.assertIn('accounts/profile', self.browser.current_url)
