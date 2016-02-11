# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

from .base import FunctionalTestCase
from . import pages
from . import remote

import projects.factories

class ActionPageTests(FunctionalTestCase):
    def test_can_add_items_to_action_list(self):
        # Alice visits the website
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        # In the sidebar she finds an action list link and she clicks it
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # On the new page there is a text box where she is invited to enter
        # a new action item
        self.assertEqual(self.browser.title, 'Actions')
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
        self.create_action('alice', 'Pet the cat')
        self.create_action('alice', 'Repaint the bed')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        # The items are both on the page
        self.assertIn('Pet the cat',
            action_page.list_text(action_page.thelist))
        self.assertIn('Repaint the bed',
            action_page.list_text(action_page.thelist))

        # Bob is another user who goes to the action list page on the site
        self.browser.quit()
        self.browser = self.webdriver()
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
        self.create_action('alice', 'Check this action')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # There is an action on the page (created earlier)
        action_page = pages.projects.ActionlistPage(self.browser)
        self.assertIn('Check this action',
            action_page.list_text(action_page.thelist))

        # She moves her mouse over the text and sees that it gets crossed out
        item = action_page.get_list_rows(action_page.thelist)[0]
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'none')
        chain = webdriver.ActionChains(self.browser)
        chain.move_to_element(item['text'])
        chain.perform()
        self.assertEqual(item['item'].value_of_css_property('text-decoration'),
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
        self.create_action('alice', 'Uncomplete this action')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She adds an item to the action page and completes it
        action_page = pages.projects.ActionlistPage(self.browser)
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
        self.create_action('alice', 'Create actions')
        self.create_action('alice', 'Remove an action')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # There are two items to the action_page
        action_page = pages.projects.ActionlistPage(self.browser)
        self.assertIn('Create actions',
            action_page.list_text(action_page.thelist))
        self.assertIn('Remove an action',
            action_page.list_text(action_page.thelist))

        # She wants to remove the last item that she has added, so she
        # looks it up in the list and removes it
        actions = action_page.get_list_rows(action_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Remove an action':
                self.assertEqual('Delete',
                    elems['delete'].get_attribute('title'))
                elems['delete'].click()
                break

        # She ends up on a new page that asks her if she wants to confirm
        # to delete the item, she first checks whether the item is correct
        self.assertEqual(self.browser.title, 'Delete action')
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
        self.create_action('alice', 'Complete action')
        self.create_action('alice', 'Remove completed action')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)

        # Make sure the actions have been added
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
                self.assertEqual('Delete',
                    elems['delete'].get_attribute('title'))
                elems['delete'].click()
                break

        # She ends up on a confirmation page which has the text of the
        # item and a confirmation button on it, which she clicks
        self.assertEqual(self.browser.title, 'Delete action')
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
        self.assertEqual('Convert to action',
            inlist_page.convert_action(item).get_attribute('title'))
        inlist_page.convert_action(item).click()

        # She ends up on a new page where she can create the action
        self.assertEqual('Convert in item to action', self.browser.title)
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

    def test_converting_other_persons_inlist_item_to_action_gives_404(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Test forbidden status\n')

        # She goes to the convert page
        item = inlist_page.listrows[0]
        inlist_page.convert_action(item).click()

        ## Copy the url so Trudy can use it
        self.wait_for(lambda: self.assertIn('/convert/',
            self.browser.current_url))
        convert_url = self.browser.current_url

        # Trudy is another user who tries to mess with Alice's items
        self.browser.quit()
        self.browser = self.webdriver()
        self.create_and_login_user('trudy', 'trudy@test.org', 'trudy')

        # Trudy directly enters the url
        self.browser.get(convert_url)
        # She is greeted with a 404 Not Found error
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('404', self.browser.title)
        self.assertIn('404', body_text)
        self.assertIn('Not Found', body_text)

    def test_deleting_other_persons_action_item_returns_404(self):
        # Alice is a user who logs in and has an action on the action list
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        self.create_action('alice', 'Test forbidden status')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()
        action_page = pages.projects.ActionlistPage(self.browser)
        # She goes to the delete page for the action
        item = action_page.get_list_rows(action_page.thelist)[0]
        item['delete'].click()

        ## Copy the url so Trudy can use it
        self.wait_for(lambda: self.assertIn('/delete/',
            self.browser.current_url))
        delete_url = self.browser.current_url

        # Trudy is another user who tries to delete Alice's action
        self.browser.quit()
        self.browser = self.webdriver()
        self.create_and_login_user('trudy', 'trudy@test.org', 'trudy')

        # Trudy directly enters the url
        self.browser.get(delete_url)
        # She sees a 404 Not Found error
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('404', self.browser.title)
        self.assertIn('404', body_text)
        self.assertIn('Not Found', body_text)

    def test_cannot_delete_action_project(self):
        # Alice is a user who logs in and goes to the action project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She sees that there is no delete button on the page
        action_page = pages.projects.ProjectPage(self.browser)
        self.assertIsNone(action_page.delete)

        # Going to the delete page directly shows a 403 Forbidden error
        self.browser.get(self.browser.current_url + 'delete/')
        self.assertIn('403', page.body.text)
        self.assertIn('Forbidden', page.body.text)

    def test_cannot_edit_action_project(self):
        # Alice is a user who logs in and goes to the action project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She sees that there is no edit button on the page
        action_page = pages.projects.ProjectPage(self.browser)
        self.assertIsNone(action_page.edit)

        # Going to the edit page directly shows a 403 Forbidden error
        self.browser.get(self.browser.current_url + 'edit/')
        self.assertIn('403', page.body.text)
        self.assertIn('Forbidden', page.body.text)

    def test_action_items_can_have_a_deadline(self):
        # Alice is a user who has an item on her action list
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            create_project(self.server_host, 'alice', 'Edit action')
        else:
            projects.factories.ActionlistItemFactory(user=user,
                text='Edit action')
        page = pages.projects.BaseProjectPage(self.browser)
        page.action_link(page.sidebar).click()

        # She sees an edit button next to the item and clicks it
        project_page = pages.projects.ProjectPage(self.browser)
        item = project_page.get_list_rows(project_page.thelist)[0]
        self.assertIsNone(item['deadline'])
        item['edit'].click()

        # She ends up on an edit action page
        edit_page = pages.projects.EditActionPage(self.browser)
        # The edit action page allows moving of the action
        self.assertIsNotNone(edit_page.select)

        # There is also a field to edit a date and time for a deadline
        self.assertIn('Deadline', edit_page.content.text)
        # She enters a date into the field and submits the form
        edit_page.deadline_date.send_keys('1970-01-01')
        edit_page.deadline_time.send_keys('00:00:00')
        edit_page.confirm.click()

        # Alice returns to the action list page, where the item has a
        # deadline on it
        item = project_page.get_list_rows(project_page.thelist)[0]
        self.assertEqual('Jan. 1, 1970, midnight', item['deadline'].text)

        # When she adds a second item it has no deadline on it
        project_page.add_box.send_keys('Write a novel\n')
        self.assertIn('Write a novel',
            project_page.list_text(project_page.thelist))
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, item in actions.items():
            if item['text'].text == 'Write a novel':
                break
        self.assertIsNone(item['deadline'])

        # Alice goes to enter a deadline for that item as well
        item['edit'].click()
        edit_page.deadline_date.send_keys('2000-01-01')
        edit_page.deadline_time.send_keys('00:00:00\n')

        # When she returns to the action list she sees that both items
        # have different dates
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, item in actions.items():
            if item['text'].text == 'Edit action':
                self.assertEqual('Jan. 1, 1970, midnight',
                    item['deadline'].text)
            elif item['text'].text == 'Write a novel':
                self.assertEqual('Jan. 1, 2000, midnight',
                    item['deadline'].text)

    def test_can_change_action_item_text(self):
        # Alice is a user who has an item on her action list
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            remote.create_action(self.server_host, 'alice', 'Play games')
        else:
            projects.factories.ActionlistItemFactory(user=user,
                text='Play games')
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.action_link(project_page.sidebar).click()

        # She sees an edit button next to it, which she clicks
        list_page = pages.projects.ProjectPage(self.browser)
        item = list_page.get_list_rows(list_page.thelist)[0]
        item['edit'].click()

        # She sees that there is a text entry field with the action's name
        # in it
        edit_page = pages.projects.EditActionPage(self.browser)
        self.assertEqual(edit_page.text_box.get_attribute('value'),
            'Play games')

        # Alice decides to change the text and saves her changes
        edit_page.text_box.clear()
        edit_page.text_box.send_keys('Play some games')
        edit_page.confirm.click()

        # She lands on the action list page and sees that her item has changed
        self.assertIn('Play some games',
            list_page.list_text(list_page.thelist))
        self.assertNotIn('Play games',
            list_page.list_text(list_page.thelist))

    def test_cannot_change_action_item_text_when_it_is_duplicate(self):
        # Alice is a user with two items on her action list
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            remote.create_action(self.server_host, 'alice', 'Save the planet')
            remote.create_action(self.server_host, 'alice',
                'Defeat the aliens')
        else:
            projects.factories.ActionlistItemFactory(user=user,
                text='Save the planet')
            projects.factories.ActionlistItemFactory(user=user,
                text='Defeat the aliens')
        project_page = pages.projects.BaseProjectPage(self.browser)
        project_page.action_link(project_page.sidebar).click()

        # Alice realises that aliens don't exist, so she wants to change
        # one of the actions
        list_page = pages.projects.ProjectPage(self.browser)
        for idx, item in list_page.get_list_rows(list_page.thelist).items():
            if item['text'].text == 'Defeat the aliens':
                item['edit'].click()
                break

        # Alice changes the item's text to be the same as the other's
        edit_page = pages.projects.EditActionPage(self.browser)
        self.assertEqual(edit_page.text_box.get_attribute('value'),
            'Defeat the aliens')
        import time
        time.sleep(5)
        edit_page.text_box.clear()
        edit_page.text_box.send_keys('Save the planet\n')

        # Instead of being send to the action list page she gets an error
        self.assertIn("This is already planned for that project",
            [error.text for error in edit_page.errors])
        self.assertEqual(len(edit_page.errors), 1)

        # When she returns to the action list without saving none of the
        # items has changed
        project_page.action_link(project_page.sidebar).click()
        self.assertIn('Save the planet',
            list_page.list_text(list_page.thelist))
        self.assertIn('Defeat the aliens',
            list_page.list_text(list_page.thelist))
        self.assertEqual(len(list_page.thelist), 2)
