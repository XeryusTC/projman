# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core import mail
from selenium.webdriver.common.keys import Keys
import re

from .base import FunctionalTestCase

User = get_user_model()

class HomePageTest(FunctionalTestCase):
    def test_can_login_from_landingpage(self):
        """Login from landing page using buildin method should be possible"""
        # Create a user account for Alice
        User.objects.create_user('alice', 'alice@test.com', 'alice')

        # Alice goes to the website
        self.browser.get(self.live_server_url)

        # The title says the name of the site
        self.assertIn('ProjMan', self.browser.title)

        # There is a header with the site's name in it, the name links
        # to the homepage
        header = self.browser.find_element_by_tag_name('header')
        logo = header.find_element_by_link_text('ProjMan')
        self.assertTrue(logo.get_attribute('href').endswith('/en/'))
        # There is also a sign in button on the header
        buttons = header.find_elements_by_tag_name('a')
        b = self.assertElementPresent(buttons, 'sign in')

        # In the main body of the site there is also a sign in button
        content = self.browser.find_element_by_id('content')
        buttons = content.find_elements_by_tag_name('a')
        self.assertElementPresent(buttons, 'sign in')

        # She clicks one of the sign in buttons and is send to the login page
        b.click()
        self.assertIn('accounts/login/', self.browser.current_url)

        # Alice logs in using her account
        login = self.browser.find_element_by_id('id_login')
        login.send_keys('alice')
        password = self.browser.find_element_by_id('id_password')
        password.send_keys('alice')
        password.send_keys(Keys.RETURN)

        # She ends up on a success page
        self.assertIn('accounts/profile/', self.browser.current_url)

    def test_can_login_using_persona_from_landingpage(self):
        """Test if we can login using persona"""
        # Alice goes to the website
        self.browser.get(self.live_server_url)

        # She clicks on a Sign in button
        buttons = self.browser.find_elements_by_tag_name('a')
        b = self.assertElementPresent(buttons, 'sign in')
        b.click()

        # She clicks on the Persona login link
        persona = self.browser.find_element_by_link_text('PERSONA')
        persona.click()

        self.switch_to_new_window('Mozilla Persona')

        # She enters her email into the persona field
        mail = self.browser.find_element_by_id('authentication_email')
        mail.send_keys('alice@mockmyid.com')
        mail.send_keys(Keys.RETURN)

        # She sees that she is logged in
        self.switch_to_new_window('ProjMan')
        self.wait_for(lambda: self.assertIn('accounts/profile/',
            self.browser.current_url), timeout=30)

    def test_register_with_django_auth_workflow(self):
        """Test if a user can register using the auth model from django"""
        # Alice goes to the website
        self.browser.get(self.live_server_url)

        # She clicks on a Sign in button
        signin = self.browser.find_element_by_link_text('SIGN IN')
        signin.click()

        # Alice doesn't have a (social media) account, so she clicks
        # the register button
        register = self.browser.find_element_by_link_text('REGISTER')
        register.click()

        # Alice fills out the form, but doesn't fill in an email
        # so she doesn't get registered
        username = self.browser.find_element_by_id('id_username')
        password1 = self.browser.find_element_by_id('id_password1')
        password2 = self.browser.find_element_by_id('id_password2')
        username.send_keys('alice')
        password1.send_keys('alice-password')
        password2.send_keys('alice-password')
        username.send_keys(Keys.RETURN)

        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('This field is required', body.text)

        # Alice fills out the form again, this time including her email
        password1 = self.browser.find_element_by_id('id_password1')
        password2 = self.browser.find_element_by_id('id_password2')
        email = self.browser.find_element_by_id('id_email')
        password1.send_keys('alice-password')
        password2.send_keys('alice-password')
        email.send_keys('alice@test.com')
        password1.send_keys(Keys.RETURN)

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
        body = self.browser.find_element_by_tag_name('body')
        self.assertIn('alice@test.com', body.text)
        confirm = self.browser.find_element_by_tag_name('button')
        self.assertIn('Confirm', confirm.text)
        confirm.click()

        # She new ends up at the profile page
        self.assertIn('accounts/profile', self.browser.current_url)
