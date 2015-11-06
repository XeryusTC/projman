# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from selenium.webdriver.common.keys import Keys

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

        # There is a header with the site's name in it
        header = self.browser.find_element_by_tag_name('header')
        self.assertIn('ProjMan', header.text)
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
        persona = self.browser.find_element_by_link_text('Persona')
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
