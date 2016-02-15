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

        # The title also changed
        self.assertEqual(self.browser.title, 'In list')

        # On the new page is a text box where she is invited to enter something
        inlist_page = pages.projects.InlistPage(self.browser)
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
        self.restart_browser()
        page = pages.projects.BaseProjectPage(self.browser)
        inlist_page = pages.projects.InlistPage(self.browser)

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

    def test_cannot_add_empty_items(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # Alice tries to add an empty item
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('')
        inlist_page.add_box.send_keys('\n')

        # She sees an error on the page
        self.assertIn('You cannot add empty items',
            [error.text for error in inlist_page.error_lists])

    def test_cannot_add_duplicate_items(self):
        self.create_and_login_user('alice', 'alice@test.com', 'alice')

        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # Alice tries to add an item
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Test duplication')
        inlist_page.add_box.send_keys(Keys.ENTER)

        # Alice tries to add the same item again
        inlist_page.add_box.send_keys('Test duplication')
        inlist_page.add_box.send_keys(Keys.ENTER)
        self.assertIn("You've already got this on your list",
            [error.text for error in inlist_page.error_lists])

    def test_can_delete_inlist_item(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds two items to the inlist
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Test deletion\n')
        inlist_page.add_box.send_keys('Remove this item\n')

        # She selects the item she added second
        second_item = [item for item in inlist_page.thelist
            if 'Remove this item' in item.text]
        self.assertEqual(len(second_item), 1)
        second_item = inlist_page.listrows[1]

        # She clicks the delete button that is next to it
        self.assertEqual('Delete',
            inlist_page.delete_item(second_item).get_attribute('title'))
        inlist_page.delete_item(second_item).click()

        # She ends up on a new page with the item name and a confirm button
        self.assertEqual(self.browser.title, 'Delete in list item')
        confirm_page = pages.projects.InlistDeletePage(self.browser)
        self.assertIn('Remove this item', confirm_page.content.text)
        # She clicks the confirm button
        confirm_page.confirm.click()

        # The item is not in the list anymore
        self.assertNotIn('Remove this item',
            [item.text for item in inlist_page.thelist])

    def test_inlist_page_has_logout_button(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.com', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She sees a logout button on the appbar and clicks it
        page.menu.click()
        page.logout.click()

        # She ends up on the confirmation page where she clicks the button
        confirmpage = pages.accounts.LogoutConfirmPage(self.browser)
        confirmpage.confirm.click()

        # She ends up on the landing page
        self.assertTrue(self.browser.current_url.endswith('/en/'))

    def test_trying_to_delete_other_persons_inlist_item_gives_404(self):
        # Alice is a user who logs in and goes to the inlist page
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.inlist_link(page.sidebar).click()

        # She adds an item
        inlist_page = pages.projects.InlistPage(self.browser)
        inlist_page.add_box.send_keys('Test forbidden status\n')

        # She goes to the delete page
        item = inlist_page.listrows[0]
        inlist_page.delete_item(item).click()
        ## We copy the URL for trudy
        self.wait_for(lambda: self.assertIn('/delete/',
            self.browser.current_url))
        delete_url = self.browser.current_url

        # Now Trudy logs in
        self.restart_browser()
        self.create_and_login_user('trudy', 'trudy@test.org', 'trudy')

        # Trudy goes directly to the delete page
        self.browser.get(delete_url)
        # She is greeted with a 404 Not Found error
        body_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('404', self.browser.title)
        self.assertIn('404', body_text)
        self.assertIn('Not Found', body_text)
