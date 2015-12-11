# -*- coding:utf-8 -*-
from selenium.webdriver.common.keys import Keys
import unittest

from .base import FunctionalTestCase
from . import pages

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
        self.assertIn('Get rich', project_page.info.text)
        self.assertIn('Become a millionaire', project_page.info.text)
        # The action she added is not on this page
        self.assertNotIn('Create a secret identity',
            project_page.list_text(project_page.thelist))

        # She clicks the link to go to the other project
        page.project_link('Save the city').click()

        # She ends up on that project's page
        self.assertIn('Save the city', project_page.info.text)
        self.assertIn('Stop the super humans', project_page.info.text)

    @unittest.expectedFailure
    def test_can_only_see_own_projects(self):
        # Alice is a user who creates some projects
        # Bob is a different user who logs in, but doesn't see Alice's
        # projects in the sidebar
        # Bob can create his own projects, those do show up in the
        # sidebar, but Alice's are still not visible
        self.fail('Implement')

    @unittest.expectedFailure
    def test_can_change_name_and_description_of_project(self):
        # Alice is a user who has a project
        # On the project page is a edit button (pencil), clicking it
        # sends her to a form where she can edit the title and
        # description of the project
        # When she submits the form she sees that the sidebar is updated
        # and so is the project page
        self.fail('Implement')

    @unittest.expectedFailure
    def test_cannot_create_project_with_empty_name(self):
        # Alice is a user who tries to create a project with an empty
        # title, which is not allowed. Trying to enter a empty description
        # is allowed
        self.fail('Implement')

    @unittest.expectedFailure
    def test_cannot_create_duplicate_projects(self):
        # Alice is a user who tries to create two projects that have the
        # same name
        # She sees an error when she tries to create the second project
        # When she creates a project with a different name but the same
        # description she is allowed to create the project
        self.fail('Implement')

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

    @unittest.expectedFailure
    def test_can_delete_project(self):
        # Alice is a user with a project
        # When she goes to the project page she sees a delete button
        # She clicks it
        # She is greeted with a confirmation page, which has the project
        # name on it
        # She clicks the confirmation button
        # The project has been removed from the sidebar
        self.fail('Implement')

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

    @unittest.expectedFailure
    def test_can_delete_action_from_project_page(self):
        # Alice is a user with a project
        # On the project there is a action, with a delete button next to
        # it, she clicks it
        # She is greeted with a confirmation page, she clicks the confirm
        # button
        # She is returned to the project page, the action is not on that
        # page anymore
        self.fail('Implement')

    @unittest.expectedFailure
    def test_can_toggle_complete_status_of_actions_on_project_page(self):
        # Alice is a user with a project
        # On the project page there is an action, when she hovers over it
        # it gets crossed out
        # She decides to click it, the action is now marked as checked
        # When she goes to hover over the item again she sees that it is
        # unmarked
        # She clicks it and the item is moved back to the incomplete
        # actions list
        self.fail('Implement')

    @unittest.expectedFailure
    def test_different_projects_can_have_duplicate_action_items(self):
        # Alice is a user with two projects
        # She goes to add an item on the first project
        # She also adds the same item on the second project, she does not
        # get an error
        # When she goes to delete the action on the first project it is
        # still kept on the second project
        self.fail('Implement')

    @unittest.expectedFailure
    def test_can_logout_from_project_page(self):
        # Alice is a user with a project
        # When she is on the project's page she sees the logout button on
        # the top right
        # She clicks it and she is logged out
        self.fail('Implement')

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
