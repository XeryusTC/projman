# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import unittest

from .base import FunctionalTestCase
from . import pages
from . import remote
from projects import factories

class ProjectsPageTests(FunctionalTestCase):
    def test_projects_can_be_created_from_scratch(self):
        # Alice is a user
        self.create_and_login_user('alice', 'alice@test.org', 'alice')

        # She sees a create project button in the sidebar and clicks it
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()

        # She ends up on a page with a form that allows her to enter a
        # name and a description
        self.assertEqual(self.browser.title, 'Create project')
        self.assertIn('Create project', page.content.text)
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Save the city')
        create_page.description_box.send_keys('Stop the super humans')

        # Completing the form redirects her to a new page
        create_page.create_button.click()

        # The new page shows the title and the description
        project_page = pages.projects.ProjectPage(self.browser)
        self.assertEqual(self.browser.title, 'Save the city')
        self.assertIn('Save the city', project_page.info.text)
        self.assertIn('Stop the super humans', project_page.info.text)

        # On the new page there is an add action box
        self.assertEqual(project_page.add_box.get_attribute('placeholder'),
            'What do you need to do?')
        # She enters some text and hits enter
        project_page.add_box.send_keys('Create a secret identity')
        project_page.add_box.send_keys(Keys.RETURN)

        # She stays on the page and sees that an action item has been added
        self.assertIn('Create a secret identity',
            project_page.list_text(project_page.thelist))
        self.assertIn('Save the city', project_page.info.text)
        self.assertIn('Stop the super humans', project_page.info.text)

        # She also sees that the project has ended up in the sidebar
        self.assertIn('Save the city', page.sidebar.text)

        # She goes to create a second project
        page.create_project_link(page.sidebar).click()
        create_page.name_box.send_keys('Get rich')
        create_page.description_box.send_keys('Become a millionaire')
        create_page.name_box.send_keys(Keys.RETURN)

        # She ends up on the new project's page
        self.assertEqual(self.browser.title, 'Get rich')
        self.assertIn('Get rich', project_page.info.text)
        self.assertIn('Become a millionaire', project_page.info.text)
        # The action she added is not on this page
        self.assertNotIn('Create a secret identity',
            project_page.list_text(project_page.thelist))

        # She clicks the link to go to the other project
        page.project_link('Save the city').click()

        # She ends up on that project's page
        self.assertEqual(self.browser.title, 'Save the city')
        self.assertIn('Save the city', project_page.info.text)
        self.assertIn('Stop the super humans', project_page.info.text)

    def test_can_only_see_own_projects(self):
        # Alice is a user who creates some projects
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()

        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Destroy all humans\n')
        project_page = pages.projects.ProjectPage(self.browser)
        self.assertIn('Destroy all humans', project_page.info.text)

        page.create_project_link(page.sidebar).click()
        create_page.name_box.send_keys('Buy an aquarium\n')
        self.assertIn('Buy an aquarium', project_page.info.text)

        # Bob is a different user who logs in
        self.browser.quit()
        self.browser = webdriver.Firefox()
        page = pages.projects.BaseProjectPage(self.browser)
        create_page = pages.projects.CreateProjectPage(self.browser)
        project_page = pages.projects.ProjectPage(self.browser)
        self.create_and_login_user('bob', 'bob@test.org', 'bob')

        # Bob doesn't see any of Alice's projects in the sidebar
        self.assertIsNone(page.project_link('Destroy all humans'))
        self.assertIsNone(page.project_link('Buy an aquarium'))

        # When Bob creates his own project page it shows up in the sidebar
        page.create_project_link(page.sidebar).click()
        create_page.name_box.send_keys('Buy a new car\n')
        self.assertIn('Buy a new car', project_page.info.text)

        # He sees that his project is in the sidebar, but Alice's are not
        self.assertIsNotNone(page.project_link('Buy a new car'))
        self.assertIsNone(page.project_link('Destroy all humans'))
        self.assertIsNone(page.project_link('Buy an aquarium'))

    def test_can_change_name_and_description_of_project(self):
        # Alice is a user who has a project
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            remote.create_project(self.server_host, 'alice', 'Build a website',
                'Make a website that is better than all others')
        else:
            factories.ProjectFactory(user=user, name='Build a website',
                description='Make a website that is better than all others')
        self.browser.refresh()

        # She navigates to the project
        page = pages.projects.BaseProjectPage(self.browser)
        page.project_link('Build a website').click()

        # On the project page is an edit button, she clicks it
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.edit.click()

        # She ends up on a page with a form that has the projects name and
        # description on it
        edit_page = pages.projects.EditPage(self.browser)
        self.assertEquals(edit_page.name.get_attribute('value'),
            'Build a website')
        self.assertEquals(edit_page.description.get_attribute('value'),
            'Make a website that is better than all others')

        # She changes both texts
        edit_page.name.clear()
        edit_page.name.send_keys('Build the best website')
        edit_page.description.clear()
        edit_page.description.send_keys('There should be no better site')

        # When completing the form she is returned to the project page
        edit_page.confirm.click()
        self.assertIn('Build the best website', project_page.info.text)
        self.assertIn('There should be no better site', project_page.info.text)
        # The name of the project is also in the sidebar
        self.assertIsNone(page.project_link('Build a website'))
        self.assertIsNotNone(page.project_link('Build the best website'))

    def test_cannot_create_project_with_empty_name(self):
        # Alice is a user who goes to the project creation page
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()

        # She tries to create a project with an emtpy name
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.create_button.click()

        # She sees that she is not allowed to do this
        self.assertIn('You cannot create a project without a name',
            [error.text for error in create_page.error_lists])

        # She goes to enter a name, but doesn't enter a description
        create_page.name_box.send_keys('Destroy all humans\n')

        # This time it is successful, so she gets redirected to the
        # project page
        project_page = pages.projects.ProjectPage(self.browser)
        self.assertIn('/projects/project/', self.browser.current_url)
        self.assertIn('Destroy all humans', project_page.info.text)

    def test_cannot_create_duplicate_projects(self):
        # Alice is a user who goes to the project creation page
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()

        # She creates a project
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Buy an aquarium')
        create_page.description_box.send_keys('I like turtles')
        create_page.create_button.click()

        # She is redirected to the project page
        project_page = pages.projects.ProjectPage(self.browser)
        self.assertIn('Buy an aquarium', project_page.info.text)
        self.assertIn('I like turtles', project_page.info.text)

        # Because she is forgetful she goes to create the same project again
        page.create_project_link(page.sidebar).click()
        create_page.name_box.send_keys('Buy an aquarium')
        create_page.description_box.send_keys('I like turtles\n')

        # This time she isn't redirected to the project page but is shown
        # an error
        self.assertTrue(self.browser.current_url.endswith('/project/create/'))
        self.assertIn('You already have this project',
            [error.text for error in create_page.error_lists])

        # She decides to update the name but not the description
        create_page.name_box.send_keys(' for the turtles\n')

        # This time she isn't greeted with an error but with a new project
        self.assertIn('Buy an aquarium for the turtles',
            project_page.info.text)
        self.assertIn('I like turtles', project_page.info.text)

    @unittest.expectedFailure
    def test_can_convert_inlist_item_into_project(self):
        # Alice is a user who logs in and creates an inlist item
        # Next to the inlist item is a conver to project page
        # She ends up on the create a project page where the title is
        # already set to the inlist item text
        # When she clicks create she is send to the project page with
        # the relevant details
        # Alice goes back to the inlist, she finds that the item has
        # been removed
        self.fail('Implement')

    def test_can_delete_project(self):
        # Alice is a user with a project
        user = self.create_and_login_user('alice', 'alice@test.org', 'alice')
        if self.against_staging:
            remote.create_project(self.server_host, 'alice',
                'Delete this project', 'Testing deletion of a project')
        else:
            factories.ProjectFactory(user=user, name='Delete this project',
                description='Testing deletion of a project')
        self.browser.refresh()

        # She navigates to the project
        page = pages.projects.BaseProjectPage(self.browser)
        page.project_link('Delete this project').click()

        # On the project page is a delete button, she clicks it
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.delete.click()

        # She is greeted with a confirmation page, which has the project
        # name on it
        confirm_page = pages.projects.ProjectDeletePage(self.browser)
        self.assertIn('Delete this project', confirm_page.content.text)
        # The project name is also in the title
        self.assertIn('Delete this project', self.browser.title)

        # She clicks the the confirm button
        confirm_page.confirm.click()

        # She is returned to a different page and the project has been
        # removed from the sidebar
        self.assertIsNone(page.project_link('Delete this project'))

    @unittest.expectedFailure
    def test_can_add_action_item_to_project(self):
        # Alice is a user with a project, she navigates to that page
        # She sees a text box on the page with an add button next to it
        # She enters some text and clicks the button
        # The page reloads and the text is now an action item on the page
        self.fail('Implement')

    @unittest.expectedFailure
    def test_action_items_can_be_moved_from_action_list_to_projects(self):
        # Alice is a user with a project
        # Alice creates an action on the action list
        # She sees a move action button next to the new action
        # She clicks it and is greeted with a page where she can select
        # a project (or the action list) to move to
        # She selects the project and clicks send
        # She is send to the action list, where the item has disapeared
        # When she goes to the project page she sees the item there
        self.fail('Implement')

    @unittest.expectedFailure
    def test_action_items_can_be_moved_from_projects_to_action_list(self):
        # Alice is a user with a project with some actions on it
        # She clicks the move action button next to one of the actions
        # She is greeted with the move page where she selects the action
        # list page and clicks the confirm button
        # She is send back to the project page, where the other actions
        # still are present
        # She navigates to the action list where she finds the action
        self.fail('Implement')

    @unittest.expectedFailure
    def test_action_items_can_be_moved_between_projects(self):
        # Alice is a user with two projects, both with actions in them
        # She navigates to the first project, selects an action to move
        # She selects the other project from the move page and clicks the
        # confirm button
        # She is send back to the original project, where the action has
        # disapeared
        # She goes to the other project page where she finds the action
        self.fail('Implement')

    @unittest.expectedFailure
    def test_cannot_move_actions_when_actions_are_duplicate(self):
        # Alice is a user with a project with an action on it
        # On the action list is an action with the same text
        # She tries to move the action to the project
        # She is greeted with a duplicate action error
        self.fail('Implement')

    def test_can_delete_action_from_project_page(self):
        # Alice is a user with a project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Catch some salamanders\n')

        # On the project page she creates an action
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.add_box.send_keys('Find a place where salamanders live')
        project_page.add_button.click()
        project_page.add_box.send_keys('Buy some boxes\n')

        # She realises that she already knows where they live, so she
        # removes the action
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Find a place where salamanders live':
                elems['delete'].click()
                break

        # She ends up on a confirmation page that asks here if she is sure
        # that she wants to remove this item. The page names the action
        # and the action it belongs to
        self.assertEqual(self.browser.title, 'Delete action')
        confirm_page = pages.projects.ActionDeletePage(self.browser)
        self.assertIn('Find a place where salamanders live',
            confirm_page.content.text)
        self.assertIn('Catch some salamanders', confirm_page.content.text)
        # She clicks the button on the page
        confirm_page.confirm.click()

        # She is redirected to the project page, where she finds that
        # there is only one action left
        self.assertIn('Catch some salamanders', project_page.info.text)
        self.assertIn('Buy some boxes',
            project_page.list_text(project_page.thelist))
        self.assertNotIn('Find a place where salamanders live',
            project_page.list_text(project_page.thelist))

    def test_can_toggle_complete_status_of_actions_on_project_page(self):
        # Alice is a user with a project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Pet the cats\n')

        # On the project page she creates an action
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.add_box.send_keys('Pet Felix\n')
        project_page.add_box.send_keys('Pet Garfield\n')

        # The 'Pet Felix' item should be on the page
        self.assertIn('Pet Felix',
            project_page.list_text(project_page.thelist))
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Pet Felix':
                item = elems

        # She hovers over the 'Pet Felix' action and sees that it gets
        # crossed out
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'none')
        chain = webdriver.ActionChains(self.browser)
        chain.move_to_element(item['text'])
        chain.perform()
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'line-through')
        # Her cursor has changed into a hand
        self.assertEqual(item['text'].value_of_css_property('cursor'),
            'pointer')

        # When she clicks it the page reloads and the action is "checked"
        item['text'].click()
        self.assertEqual(self.browser.title, 'Pet the cats')
        self.assertIn('Pet Felix',
            project_page.list_text(project_page.checked_list))

        ## The item needs to be found again because the page reloaded
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Pet Felix':
                item = elems

        ## Move the curser away from where the element was
        chain = webdriver.ActionChains(self.browser)
        chain.move_to_element(page.sidebar)
        chain.perform()

        # When she hovers over the action she sees that it gets uncrossed
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'line-through')
        chain = webdriver.ActionChains(self.browser)
        chain.move_to_element(item['text'])
        chain.perform()
        self.assertEqual(item['text'].value_of_css_property('text-decoration'),
            'none')
        self.assertEqual(item['text'].value_of_css_property('cursor'),
            'pointer')

        # After she clicks it the item is marked as unchecked
        item['text'].click()
        self.assertListEqual([], project_page.checked_list)

    def test_different_projects_can_have_duplicate_action_items(self):
        # Alice is a user who goes to create a project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Plan a holiday\n')

        # She adds an action on the page
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.add_box.send_keys('Save money\n')
        # The item ends up on the page
        self.assertIn('Save money',
            project_page.list_text(project_page.thelist))

        # She goes to create another project
        page.create_project_link(page.sidebar).click()
        create_page.name_box.send_keys('Buy a new car\n')
        # There is no action item here yet
        self.assertEqual([], project_page.thelist)
        # She creates an identical action for this project
        project_page.add_box.send_keys('Save money\n')
        # The item got added without error
        self.assertEqual([], project_page.error_lists)
        self.assertIn('Save money',
            project_page.list_text(project_page.thelist))

        # Alice goes back to the first project she created
        page.project_link('Plan a holiday').click()
        # She goes to delete the save money item for this project
        actions = project_page.get_list_rows(project_page.thelist)
        for idx, elems in actions.items():
            if elems['text'].text == 'Save money':
                elems['delete'].click()
                break
        # She confirms that she wants to delete the action
        confirm_page = pages.projects.ActionDeletePage(self.browser)
        confirm_page.confirm.click()

        # She is returned to the project and the action is gone
        self.assertEqual(self.browser.title, 'Plan a holiday')
        self.assertNotIn('Save money',
            project_page.list_text(project_page.thelist))

        # When she goes to the other project the action is still there
        page.project_link('Buy a new car').click()
        self.assertEqual(self.browser.title, 'Buy a new car')
        self.assertIn('Save money',
            project_page.list_text(project_page.thelist))

    def test_can_logout_from_project_page(self):
        # Alice is a user with a project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Catch up on tv\n')

        # There is a log out button visible, she clicks it
        page.logout.click()

        # She lands on the logout confirmation page
        confirm_page = pages.accounts.LogoutConfirmPage(self.browser)
        confirm_page.confirm.click()

        # She sees that she is on the landing page
        self.assertTrue(self.browser.current_url.endswith('/en/'))

    def test_can_logout_from_create_project_page(self):
        # Alice is a user who goes to the create project page
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()

        # She sees the log out button and clicks it
        page.logout.click()

        # She lands on the logout confirmation page
        confirm_page = pages.accounts.LogoutConfirmPage(self.browser)
        confirm_page.confirm.click()

        # She sees that she is on the landing page
        self.assertTrue(self.browser.current_url.endswith('/en/'))

    @unittest.expectedFailure
    def test_deleting_other_persons_project_retuns_403(self):
        # Alice is a user with a project
        # Trudy enters the delete project url for Alice's project
        # She is greeted with a 403 Forbidden message
        self.fail('Implement')

    @unittest.expectedFailure
    def test_changing_other_persons_project_details_returns_403(self):
        # Alice is a user with a project
        # Trudy enters the change project details url for Alice's project
        # She is greeted with a 403 Forbidden message
        self.fail('Implement')

    def test_project_action_items_do_not_show_on_action_list(self):
        # Alice is a user who creates a project
        self.create_and_login_user('alice', 'alice@test.org', 'alice')
        page = pages.projects.BaseProjectPage(self.browser)
        page.create_project_link(page.sidebar).click()
        create_page = pages.projects.CreateProjectPage(self.browser)
        create_page.name_box.send_keys('Plan holiday\n')

        # On the project page she creates an action
        project_page = pages.projects.ProjectPage(self.browser)
        project_page.add_box.send_keys('Save money\n')
        project_page.add_box.send_keys('Figure out where to go\n')

        # The items appear on the page
        self.assertIn('Save money',
            project_page.list_text(project_page.thelist))
        self.assertIn('Figure out where to go',
            project_page.list_text(project_page.thelist))

        # She goes to the action list page
        page.action_link(page.sidebar).click()

        # The items are not on this page
        self.assertNotIn('Save money',
            project_page.list_text(project_page.thelist))
        self.assertNotIn('Figure out where to go',
            project_page.list_text(project_page.thelist))
