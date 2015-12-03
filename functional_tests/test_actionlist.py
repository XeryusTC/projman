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
        self.assertIn('Test the action list',
            action_page.list_text(action_page.thelist))

        # She decides to add a second item to the list
        action_page.add_box.send_keys('Ride the comet')
        action_page.add_button.click()

        # The page reloads again and now both items are on the page
        self.assertIn('Test the action list',
            action_page.list_text(action_page.thelist))
        self.assertIn('Ride the comet',
            action_page.list_text(action_page.thelist))

    def test_action_list_items_are_not_visible_for_other_users(self):
        # Alice visits the website and creates an item for the action list
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Pet the cat\n')
        action_page.add_box.send_keys('Repaint the bed\n')
        # The items are both on the page
        self.assertIn('Pet the cat',
            action_page.list_text(action_page.thelist))
        self.assertIn('Repaint the bed',
            action_page.list_text(action_page.thelist))

        # Bob is another user who goes to the action list page on the site
        self.browser.quit()
        self.browser = webdriver.Firefox()
        page = pages.projects.BaseProjectPage(self.browser)
        action_page = pages.projects.ActionlistPage(self.browser)

        self.create_and_login_user('bob', 'bob@test.com', 'bob')
        page.action_link(page.sidebar).click()

        # He cannot see Alice's items
        self.assertNotIn('Pet the cat',
            action_page.list_text(action_page.thelist))
        self.assertNotIn('Repaint the bed',
            action_page.list_text(action_page.thelist))

        # Bob enters some items of his own
        action_page.add_box.send_keys('Eat some sushi')
        action_page.add_box.send_keys(Keys.ENTER)

        # There is still no sign of Alice's list, but Bob can see the item
        # that he just added
        self.assertNotIn('Pet the cat',
            action_page.list_text(action_page.thelist))
        self.assertNotIn('Repaint the bed',
            action_page.list_text(action_page.thelist))
        self.assertIn('Eat some sushi',
            action_page.list_text(action_page.thelist))

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

    def test_can_complete_action_item(self):
        # Alice is a user who logs in and goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She adds an item to the action page
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Check this action\n')

        # The element should end up on the page
        self.assertIn('Check this action',
            action_page.list_text(action_page.thelist))

        # She moves her mouse over the text and sees that it gets crossed out
        item = action_page.get_list_rows(action_page.thelist)[0]
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'none')
        chain = webdriver.ActionChains(self.browser)
        chain.move_to_element(item['text'])
        chain.perform()
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'line-through')
        # She also notices that her curser indicates that she can click it
        self.assertEqual(item['text'].value_of_css_property('cursor'), 'pointer')

        # When she clicks it the page reloads and the action is "checked"
        item['text'].click()
        self.assertIn('Check this action',
            action_page.list_text(action_page.checked_list))

    def test_can_undo_completed_action_item(self):
        # Alice is a user who logs in and goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She adds an item to the action page and completes it
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Uncomplete this action\n')
        action_page.get_list_rows(action_page.thelist)[0]['text'].click()

        # The item is in the completed list
        self.assertIn('Uncomplete this action',
            action_page.list_text(action_page.checked_list))

        # She clicks the item in the complete list
        action_page.get_list_rows(action_page.checked_list)[0]['text'].click()

        # The item is back in the incomplete list
        self.assertIn('Uncomplete this action',
            action_page.list_text(action_page.thelist))

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
        self.assertIn('Create actions',
            action_page.list_text(action_page.thelist))
        self.assertIn('Remove an action',
            action_page.list_text(action_page.thelist))

        # She wants to remove the last item that she has added, so she
        # looks it up in the list and removes it
        actions = action_page.get_list_rows(action_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Remove an action':
                elems['delete'].click()
                break

        # She ends up on a new page that asks her if she wants to confirm
        # to delete the item, she first checks whether the item is correct
        confirm_page = pages.projects.ActionDeletePage(self.browser)
        self.assertIn('Remove an action', confirm_page.content.text)
        # She clicks the confirm button
        confirm_page.confirm.click()

        # She is returned to the action list page, which doesn't have the
        # item anymore, but the other one is still there
        self.assertIn('Create actions',
            action_page.list_text(action_page.thelist))
        self.assertNotIn('Remove an action',
            action_page.list_text(action_page.thelist))

    def test_can_delete_completed_action_items(self):
        # Alice is a user who logs in and goes to the action list page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        action_page.add_box.send_keys('Complete action\n')
        action_page.add_box.send_keys('Remove completed action\n')

        # Make sure the elements are added
        self.assertIn('Complete action',
            action_page.list_text(action_page.thelist))
        self.assertIn('Remove completed action',
            action_page.list_text(action_page.thelist))

        # Alice goes to complete the first action she's added
        actions = action_page.get_list_rows(action_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Complete action':
                elems['text'].click()
                break

        # The item is now in the completed list next to a delete button,
        # she clicks it
        actions = action_page.get_list_rows(action_page.checked_list)
        for idx, elems in actions.items():
            if elems['text'].text == 'Complete action':
                elems['delete'].click()
                break

        # She ends up on a confirmation page which has the text of the
        # item and a confirmation button on it, which she clicks
        confirm_page = pages.projects.ActionDeletePage(self.browser)
        self.assertIn('Complete action', confirm_page.content.text)
        confirm_page.confirm.click()

        # She is returned to the action list page, which doesn't have the
        # item in either list anymore
        self.assertIn('Remove completed action',
            action_page.list_text(action_page.thelist))
        self.assertNotIn('Complete action',
            action_page.list_text(action_page.thelist))
        self.assertNotIn('complete action',
            action_page.list_text(action_page.checked_list))

    def test_can_change_inlist_items_into_action_item(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item to the inlist page
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Create action\n')
        self.assertIn('Create action',
            [item.text for item in inlist_page.thelist])

        # There is a button next to it that lets her convert it to an
        # action, she clicks it
        item = inlist_page.listrows[0]
        inlist_page.convert_action(item).click()

        # She ends up on a new page where she can create the action
        convert_page = pages.projects.ConvertToActionPage(self.browser)
        # The text box holds the text from the inlist item
        self.assertEqual(convert_page.text_box.get_attribute('value'),
            'Create action')

        # She enters a new text
        convert_page.text_box.clear()
        convert_page.text_box.send_keys('Create an action')

        # She clicks the convert button, which saves the action
        convert_page.convert_button.click()

        # She returns to the linst page
        self.assertTrue(
            self.browser.current_url.endswith('/projects/inlist/'))
        # When she navigates to the action page she finds the item there
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        self.assertIn('Create an action',
            action_page.list_text(action_page.thelist))

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
        self.assertNotIn('Inlist item',
            action_page.list_text(action_page.thelist))

        # She adds an item on the action page
        action_page.add_box.send_keys('Action list item\n')
        self.assertIn('Action list item',
            action_page.list_text(action_page.thelist))

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
