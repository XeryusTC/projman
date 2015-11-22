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
        action_page = pages.projects.ActionlistPage(self.browser)
        self.assertEqual(action_page.add_box.get_attribute('placeholder'),
            'What do you need to do?')
        # She enters something in the text box and hits enter
        action_page.add_box.send_keys('Test the action list')
        action_page.add_box.send_keys(Keys.RETURN)

        # The page reloads and she sees that the item is in a list on the page
        self.assertIn('Test the action list', action_page.list_text)

        # She decides to add a second item to the list
        action_page.add_box.send_keys('Ride the comet')
        action_page.add_button.click()

        # The page reloads again and now both items are on the page
        self.assertIn('Test the action list', action_page.list_text)
        self.assertIn('Ride the comet', action_page.list_text)

    def test_action_list_items_are_not_visible_for_other_users(self):
        # Alice visits the website and creates an item for the action list
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Pet the cat\n')
        action_page.add_box.send_keys('Repaint the bed\n')
        # The items are both on the page
        self.assertIn('Pet the cat', action_page.list_text)
        self.assertIn('Repaint the bed', action_page.list_text)

        # Bob is another user who goes to the action list page on the site
        self.browser.quit()
        self.browser = webdriver.Firefox()
        page = pages.projects.BaseProjectPage(self.browser)
        action_page = pages.projects.ActionlistPage(self.browser)

        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page.action_link(page.sidebar).click()

        # He cannot see Alice's items
        self.assertNotIn('Pet the cat', action_page.list_text)
        self.assertNotIn('Repaint the bed', action_page.list_text)

        # Bob enters some items of his own
        action_page.add_box.send_keys('Eat some sushi')
        action_page.add_box.send_keys(Keys.ENTER)

        # There is still no sign of Alice's list, but Bob can see the item
        # that he just added
        self.assertNotIn('Pet the cat', action_page.list_text)
        self.assertNotIn('Repaint the bed', action_page.list_text)
        self.assertIn('Eat some sushi', action_page.list_text)

    def test_cannot_add_empty_items_to_action_list(self):
        # Alice is a user who goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # Alice tries to add an empty item
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('\n')

        # She sees an error on the page
        self.assertIn('You cannot add empty items',
            [error.text for error in action_page.error_lists])

    def test_cannot_add_duplicate_items_to_action_list(self):
        # Bob is a user who goes to the action list page
        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # Bob adds an item
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Test duplication\n')

        # He tries to add an item again but gets an error
        action_page.add_box.send_keys('Test duplication\n')
        self.assertIn("You already planned to do this",
            [error.text for error in action_page.error_lists])

    @unittest.expectedFailure
    def test_can_complete_action_item(self):
        self.fail('Implement this')

    def test_can_delete_action_item(self):
        # Alice is a user who logs in and goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She adds two items to the action_page
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Create actions\n')
        action_page.add_box.send_keys('Remove an action\n')

        # Wait for the elements to be added
        self.assertIn('Create actions', action_page.list_text)
        self.assertIn('Remove an action', action_page.list_text)
        self.wait_for(lambda:
            self.assertEqual(len(action_page.get_list_rows()), 2))

        # She wants to remove the last item that she has added, so she
        # looks it up in the list and removes it
        actions = action_page.get_list_rows()
        for idx, elems in actions.items():
            if elems['text'].text == 'Remove an action':
                elems['delete'].click()

        # She ends up on a new page that asks her if she wants to confirm
        # to delete the item, she first checks whether the item is correct
        confirm_page = pages.projects.ActionDeletePage(self.browser)
        self.assertIn('Remove an action', confirm_page.content.text)
        # She clicks the confirm button
        confirm_page.confirm.click()

        # She is returned to the action list page, which doesn't have the
        # item anymore, but the other one is still there
        self.assertIn('Create actions', action_page.list_text)
        self.assertNotIn('Remove an action', action_page.list_text)

    @unittest.expectedFailure
    def test_can_change_inlist_items_into_action_item(self):
        self.fail('Implement this')

    def test_action_list_and_inlist_are_separate_lists(self):
        # Alice is a user who goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item on the inlist page
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Inlist item\n')
        self.assertIn('Inlist item',
            [item.text for item in inlist_page.thelist])

        # She then goes to the action list page
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)

        # The previously added item is not on this page
        self.assertNotIn('Inlist item', action_page.list_text)

        # She adds an item on the action page
        action_page.add_box.send_keys('Action list item\n')
        self.assertIn('Action list item', action_page.list_text)

        # She navigates back to the inlist page and sees that the last
        # added item is not on that list, but the first item is
        page.inlist_link(page.sidebar).click()
        self.assertNotIn('Action list item',
            [item.text for item in inlist_page.thelist])
        self.assertIn('Inlist item',
            [item.text for item in inlist_page.thelist])

    def test_can_logout_from_action_page(self):
        # Alice is a user who goes to the actionlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # Alice can click a log out button
        page.logout.click()

        # She lands on the logout confirmation page
        confirm_page = pages.accounts.LogoutConfirmPage(self.browser)
        confirm_page.confirm.click()

        # She is now logged out and on the landing page again
        self.assertTrue(self.browser.current_url.endswith('/en/'))
