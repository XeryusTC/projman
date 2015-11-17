# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from . import pages
from .base import FunctionalTestCase

class InlistTests(FunctionalTestCase):
    def test_can_add_items_to_in_list(self):
        # Alice visits the website
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        # In the sidebar she finds an inlist link and she clicks it
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # On the new page is a text box where she is invited to enter something
        inlist_page = pages.inlist.InlistPage(self.browser)
        self.assertEqual(inlist_page.add_box.get_attribute('placeholder'),
            'What needs to be done?')
        # She enters something in the text box and hits enter
        inlist_page.add_box.send_keys('Test the website')
        inlist_page.add_box.send_keys(Keys.RETURN)

        # The page reloads and she sees that the item is in a list on the page
        self.assertIn('Test the website',
            [item.text for item in inlist_page.thelist])

        # She decides to add a second item to the list
        inlist_page.add_box.send_keys('Plan trip to Saturn')
        inlist_page.add_button.click()

        # The page reloads again and now both the items are on the page
        self.assertIn('Test the website',
            [item.text for item in inlist_page.thelist])
        self.assertIn('Plan trip to Saturn',
            [item.text for item in inlist_page.thelist])

        # Bob is another user who goes to the inlist page on the website
        # and he does not see Alice's list
        self.browser.quit()
        self.browser = webdriver.Firefox()
        page = pages.projects.BaseProjectPage(self.browser)
        inlist_page = pages.inlist.InlistPage(self.browser)

        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page.inlist_link(page.sidebar).click()
        self.assertNotIn('Test the website',
            [item.text for item in inlist_page.thelist])
        self.assertNotIn('Plan trip to Saturn',
            [item.text for item in inlist_page.thelist])

        # Bob goes to enter an item of his own
        inlist_page.add_box.send_keys('Reset the database')
        inlist_page.add_box.send_keys(Keys.ENTER)

        # There still is no sign of Alice's list, but Bob's new item is
        # visible to him
        self.assertNotIn('Test the website',
            [item.text for item in inlist_page.thelist])
        self.assertNotIn('Plan trip to Saturn',
            [item.text for item in inlist_page.thelist])
        self.assertIn('Reset the database',
            [item.text for item in inlist_page.thelist])

        # Bob tries to send an empty form, but he gets an error
        inlist_page.add_box.send_keys('')
        inlist_page.add_button.click()

        self.assertIn('You cannot add empty items',
            [error.text for error in inlist_page.error_lists])
