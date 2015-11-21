# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

from .base import FunctionalTestCase
from . import pages

class ActionPageTests(FunctionalTestCase):
    def test_can_add_items_to_action_list(self):
        # Alice visits the website
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        # In the sidebar she finds an action list link and she clicks it
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # On the new page there is a text box where she is invited to enter
        # a new action item
        action_page = pages.actionlist.ActionlistPage(self.browser)
        self.assertEqual(action_page.add_box.get_attribute('placeholder'),
            'What do you need to do?')
        # She enters something in the text box and hits enter
        action_page.add_box.send_keys('Test the action list')
        action_page.add_box.send_keys(Keys.RETURN)

        # The page reloads and she sees that the item is in a list on the page
        self.assertIn('Test the action list',
            [item.text for item in action_page.thelist])

        # She decides to add a second item to the list
        action_page.add_box.send_keys('Ride the comet')
        action_page.add_button.click()

        # The page reloads again and now both items are on the page
        self.assertIn('Test the action list',
            [item.text for item in action_page.thelist])
        self.assertIn('Ride the comet',
            [item.text for item in action_page.thelist])

    def test_action_list_items_are_not_visible_for_other_users(self):
        # Alice visits the website and creates an item for the action list
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.actionlist.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Pet the cat\n')
        action_page.add_box.send_keys('Repaint the bed\n')
        # The items are both on the page
        self.assertIn('Pet the cat',
            [item.text for item in action_page.thelist])
        self.assertIn('Repaint the bed',
            [item.text for item in action_page.thelist])

        # Bob is another user who goes to the action list page on the site
        self.browser.quit()
        self.browser = webdriver.Firefox()
        page = pages.projects.BaseProjectPage(self.browser)
        action_page = pages.actionlist.ActionlistPage(self.browser)

        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page.action_link(page.sidebar).click()

        # He cannot see Alice's items
        self.assertNotIn('Pet the cat',
            [item.text for item in action_page.thelist])
        self.assertNotIn('Repaint the bed',
            [item.text for item in action_page.thelist])

        # Bob enters some items of his own
        action_page.add_box.send_keys('Eat some sushi')
        action_page.add_box.send_keys(Keys.ENTER)

        # There is still no sign of Alice's list, but Bob can see the item
        # that he just added
        self.assertNotIn('Pet the cat',
            [item.text for item in action_page.thelist])
        self.assertNotIn('Repaint the bed',
            [item.text for item in action_page.thelist])
        self.assertIn('Eat some sushi',
            [item.text for item in action_page.thelist])

    def test_cannot_add_empty_items_to_action_list(self):
        # Alice is a user who goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # Alice tries to add an empty item
        action_page = pages.actionlist.ActionlistPage(self.browser)
        action_page.add_box.send_keys('\n')

        # She sees an error on the page
        self.assertIn('You cannod add empty action items',
            [error.text for error in action_page.error_lists])

    def test_cannot_add_duplicate_items_to_action_list(self):
        # Bob is a user who goes to the action list page
        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # Bob adds an item
        action_page = pages.actionlist.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Test duplication\n')

        # He tries to add an item again but gets an error
        action_page.add_box.send_keys('Test duplication\n')
        self.assertIn("You already planned to do this",
            [error.text for error in action_page.error_list])

    @unittest.expectedFailure
    def test_can_complete_action_item(self):
        self.fail('Implement this')

    @unittest.expectedFailure
    def test_can_delete_action_item(self):
        self.fail('Implement this')

    @unittest.expectedFailure
    def test_can_change_inlist_items_into_action_item(self):
        self.fail('Implement this')

    def test_action_list_and_inlist_are_separate_lists(self):
        # Alice is a user who goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item on the inlist page
        inlist_page = pages.inlist.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Inlist item\n')
        self.assertIn('Inlist item',
            [item.text for item in inlist_page.thelist])

        # She then goes to the action list page
        page.action_link(page.sidebar).click()
        action_page = pages.actionlist.ActionlistPage(self.browser)

        # The previously added item is not on this page
        self.assertNotIn('Inlist item',
            [item.text for item in action_page.thelist])

        # She adds an item on the action page
        action_page.add_box.send_keys('Action list item\n')
        self.assertIn('Action list item',
            [item.text for item in action_page.thelist])

        # She navigates back to the inlist page and sees that the last
        # added item is not on that list, but the first item is
        page.inlist_link(page.sidebar).click()
        self.assertNotIn('Action list item',
            [item.text for item in inlist_page.thelist])
        self.assertIn('Inlist item',
            [item.text for item in inlist_page.thelist])