# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve, reverse
from django.http.response import Http404
from django.test import TestCase
from django.utils.html import escape
from unittest import mock

from projects import factories, forms, models, views
from common.tests import ViewTestMixin

User = get_user_model()
alice = None
bob = None

def setUpModule():
    global alice, bob
    alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
    bob = User.objects.create_user('bob', 'bob@test.com', 'bob')

def tearDownModule():
    alice.delete()
    bob.delete()

class TestMainPage(ViewTestMixin, TestCase):
    explicit_url = '/en/projects/'
    templates = ('html.html', 'projects/base.html', 'projects/mainpage.html')

    def setUp(self):
        self.url = reverse('projects:main')
        self.view = views.MainPageView.as_view()


class InlistpageTest(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html', 'projects/inlist.html')

    def setUp(self):
        self.url = '/en/projects/inlist/'
        self.view = views.InlistView.as_view()

    def test_inlist_uses_inlist_form(self):
        response = self.get_request(alice)
        self.assertIsInstance(response.context_data['form'], forms.InlistForm)

    def test_displays_only_items_for_that_user(self):
        item1 = factories.InlistItemFactory(text='item 1', user=alice)
        item2 = factories.InlistItemFactory(text='item 2', user=alice)
        item3 = factories.InlistItemFactory(text='item 3', user=bob)

        response = self.get_request(alice)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_saves_POST_request_to_the_users_inlist(self):
        response = self.post_request(alice, {'text': 'ecila'})

        self.assertEqual(models.InlistItem.objects.count(), 1)
        item = models.InlistItem.objects.first()
        self.assertEqual(item.text, 'ecila')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_inlist_page(self):
        response = self.post_request(alice, {'text': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_invalid_input_saves_nothing_to_db(self):
        response = self.post_request(alice, {'text': ''})
        self.assertEqual(models.InlistItem.objects.count(), 0)

    def test_context_variable_contains_users_inlist_items(self):
        item1 = factories.InlistItemFactory(text='item 1', user=alice)
        item2 = factories.InlistItemFactory(text='item 2', user=alice)

        response = self.get_request(alice)

        self.assertIn('inlist_items', response.context_data.keys())
        self.assertIn(item1, response.context_data['inlist_items'])
        self.assertIn(item2, response.context_data['inlist_items'])

    def test_form_invalid_input_shows_error_on_page(self):
        response = self.post_request(alice, {'text': ''})

        self.assertEqual(models.InlistItem.objects.count(), 0)
        self.assertContains(response, forms.EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_item_twice_shows_error_on_page(self):
        item1 = factories.InlistItemFactory(text='dupe', user=alice)

        response = self.post_request(alice, {'text': 'dupe'})

        self.assertEqual(models.InlistItem.objects.count(), 1)
        self.assertContains(response, escape(forms.DUPLICATE_ITEM_ERROR))


class InlistItemDeleteViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/inlistitem_confirm_delete.html')

    def setUp(self):
        self.item = factories.InlistItemFactory(user=alice)
        self.url = '/en/projects/inlist/{}/delete/'.format(self.item.pk)
        self.view = views.InlistItemDelete.as_view()

    # Overwrite test from ViewTestMixin since it doesn't allow for extra
    # parameters
    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_inlist_item_delete_view_shows_item_name(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_returns_404_when_wrong_user_requests_page_with_get(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.item.pk)

    def test_returns_404_when_wrong_user_requests_page_with_post(self):
        with self.assertRaises(Http404):
            self.post_request(bob, pk=self.item.pk)


class ActionlistItemDeleteViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
            'projects/actionlistitem_confirm_delete.html')

    def setUp(self):
        self.item = factories.ActionlistItemFactory(user=alice)
        self.url = '/en/projects/actions/{}/delete/'.format(self.item.pk)
        self.view = views.ActionlistItemDelete.as_view()

    # Overwrite test from ViewTestMixin since it doesn't allow for extra
    # parameters
    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_actionlist_item_delete_view_shows_item_text(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_POST_redirects_to_action_list_for_non_project_actions(self):
        response = self.post_request(alice, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': models.get_user_action_project(alice).pk}))

    def test_POST_redirects_to_project_page_for_project_actions(self):
        project = factories.ProjectFactory(user=alice)
        item = factories.ActionlistItemFactory(user=alice, project=project)
        response = self.post_request(alice, pk=item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': project.pk}))

    def test_GET_from_different_user_shows_404(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.item.pk)

    def test_POST_from_different_user_shows_404(self):
        with self.assertRaises(Http404):
            self.post_request(bob, pk=self.item.pk)


class ActionCompleteViewTest(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/actionlistitem_errorform.html')

    def setUp(self):
        self.item = factories.ActionlistItemFactory(user=alice)
        self.url = reverse('projects:complete_action',
            kwargs={'pk': self.item.pk})
        self.explicit_url = '/en/projects/actions/{}/complete/'.format(
            self.item.pk)
        self.view = views.ActionCompleteView.as_view()


    def test_POST_changes_the_complete_status_to_true(self):
        self.assertFalse(self.item.complete)
        self.post_request(alice, pk=self.item.pk)
        self.item = models.ActionlistItem.objects.get(pk=self.item.pk)
        self.assertTrue(self.item.complete)

    def test_POST_toggles_the_complete_status(self):
        self.assertFalse(self.item.complete)
        self.item.complete = True
        self.item.save()
        self.assertTrue(models.ActionlistItem.objects.get(pk=self.item.pk))

        self.post_request(alice, pk=self.item.pk)

        item = models.ActionlistItem.objects.get(pk=self.item.pk)
        self.assertFalse(item.complete)

    def test_only_owner_can_change_complete_status(self):
        response = self.post_request(bob, pk=self.item.pk)
        self.assertContains(response, forms.ILLEGAL_ACTION_ERROR)

    def test_redirects_to_action_list_when_project_not_set_on_action(self):
        response = self.post_request(alice, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': self.item.project.pk}))

    def test_redirects_to_project_page_when_action_has_project(self):
        project = factories.ProjectFactory(user=alice)
        item = factories.ActionlistItemFactory(user=alice, project=project)
        response = self.post_request(alice, pk=item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('projects:project', kwargs={'pk': project.pk}))


class ConvertInlistItemToActionItemTest(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/convert_inlist_to_action.html')

    def setUp(self):
        self.item = factories.InlistItemFactory(user=alice)
        self.url = reverse('projects:convert_inlist_action',
            kwargs={'pk': self.item.pk})
        self.view = views.InlistItemToActionView.as_view()

    def test_uses_correct_form_class(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.ConvertInlistToActionForm)

    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('account_login') + '?next=' + self.url)

    def test_shows_item_text_on_page(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_returns_404_when_item_does_not_exist(self):
        self.item.delete()
        with self.assertRaises(Http404):
            response = self.get_request(alice, pk=self.item.pk)

    def test_POST_request_saves_to_actionlist(self):
        self.assertEqual(models.ActionlistItem.objects.count(), 0)
        response = self.post_request(alice, {'text': 'test'}, pk=self.item.pk)
        self.assertEqual(models.ActionlistItem.objects.count(), 1)

    def test_POST_request_deletes_inlist_item(self):
        self.assertEqual(models.InlistItem.objects.count(), 1)
        response = self.post_request(alice, {'text': 'test'}, pk=self.item.pk)
        self.assertEqual(models.InlistItem.objects.count(), 0)

    def test_displays_error_when_text_is_empty(self):
        response = self.post_request(alice, {'text': ''}, pk=self.item.pk)
        self.assertContains(response, forms.EMPTY_TEXT_ERROR)

    def test_displays_error_when_item_has_duplicate_action_text(self):
        factories.ActionlistItemFactory(user=alice, text='duplo')
        response = self.post_request(alice, data={'text': 'duplo'},
            pk=self.item.pk)
        self.assertContains(response, forms.DUPLICATE_ACTION_ERROR)

    def test_redirects_to_inlist_page(self):
        response = self.post_request(alice, {'text': 'test'}, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:inlist'))

    def test_get_request_from_wrong_user_returns_404(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.item.pk)

    def test_post_request_from_wrong_user_returns_404(self):
        with self.assertRaises(Http404):
            self.post_request(bob, pk=self.item.pk)


class ProjectViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html', 'projects/project.html')

    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:project', kwargs={'pk':self.project.pk})
        self.view = views.ProjectView.as_view()

    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_shows_project_name(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertContains(response, self.project.name)

    def test_shows_project_description(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertContains(response, self.project.description)

    def test_uses_actionlist_form(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.ActionlistForm)

    def test_POST_request_saves_to_project(self):
        response = self.post_request(alice, {'text': 'dinosaur'},
            pk=self.project.pk)

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        item = models.ActionlistItem.objects.first()
        self.assertEqual(item.text, 'dinosaur')
        self.assertEqual(item.user, alice)
        self.assertEqual(item.project, self.project)
        self.assertSequenceEqual(self.project.action_list.all(), [item])

    def test_POST_request_redirects_to_project(self):
        response = self.post_request(alice, {'text': 'misquito'},
            pk=self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_empty_input_saves_nothing_to_db(self):
        response = self.post_request(alice, {'text': ''}, pk=self.project.pk)
        self.assertEqual(models.ActionlistItem.objects.count(), 0)

    def test_empty_input_shows_error_on_page(self):
        response = self.post_request(alice, {'text': ''}, pk=self.project.pk)
        self.assertContains(response, forms.EMPTY_TEXT_ERROR)

    def test_duplicate_text_saves_nothing_to_db(self):
        item1 = factories.ActionlistItemFactory(text='dupe', user=alice,
            project=self.project)
        response = self.post_request(alice, {'text': 'dupe'},
            pk=self.project.pk)
        self.assertEqual(models.ActionlistItem.objects.count(), 1)

    def test_duplicate_text_shows_error_on_page(self):
        item1 = factories.ActionlistItemFactory(text='dupe', user=alice,
            project=self.project)
        response = self.post_request(alice, {'text': 'dupe'},
            pk=self.project.pk)
        self.assertContains(response, forms.DUPLICATE_ACTION_ERROR)

    def test_contains_all_actions_in_context_actionlist(self):
        nc = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=False, project=self.project)
        co = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=False, project=self.project)

        response = self.get_request(alice, pk=self.project.pk)

        context = response.context_data['project']
        self.assertEqual(context.action_list.count(), len(nc) + len(co))
        self.assertIn(nc[0], context.action_list.all())
        self.assertIn(nc[1], context.action_list.all())
        self.assertIn(co[0], context.action_list.all())
        self.assertIn(co[1], context.action_list.all())

    def test_notifies_when_project_is_users_action_project(self):
        project = models.get_user_action_project(alice)
        response = self.get_request(alice, pk=project.pk)
        self.assertTrue(response.context_data['protected'])

    def test_non_action_projects_are_not_protected(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertFalse(response.context_data['protected'])

    def test_GET_request_shows_404_error_ion_wrong_user_request(self):
        with self.assertRaises(Http404):
            response = self.get_request(bob, pk=self.project.pk)

    def test_POST_request_shows_404_error_on_wrong_user_request(self):
        with self.assertRaises(Http404):
            response = self.post_request(bob, pk=self.project.pk)


class CreateProjectViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/create_project.html')

    def setUp(self):
        self.url = reverse('projects:create_project')
        self.view = views.CreateProjectView.as_view()

    def test_uses_create_project_form(self):
        response = self.get_request(alice)
        self.assertIsInstance(response.context_data['form'],
            forms.CreateProjectForm)

    def test_POST_request_saves_to_user(self):
        response = self.post_request(alice, {'name': 'Watch videos'})
        self.assertEqual(models.Project.objects.count(), 3)
        item = models.Project.objects.get(name='Watch videos')
        self.assertEqual(item.name, 'Watch videos')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_project_page(self):
        response = self.post_request(alice, {'name': 'Watch videos'})
        project = models.Project.objects.get(name='Watch videos')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('projects:project', kwargs={'pk':project.pk}))

    def test_empty_name_saves_nothing_to_db(self):
        response = self.post_request(alice, {'name': ''})
        self.assertEqual(models.Project.objects.count(), 2)

    def test_empty_name_shows_error_on_page(self):
        response = self.post_request(alice, {'name': ''})
        self.assertContains(response, forms.EMPTY_PROJECT_NAME_ERROR)

    def test_duplicate_name_saves_nothing_to_db(self):
        factories.ProjectFactory(name='dupe', user=alice)
        response = self.post_request(alice, {'name': 'dupe'})
        self.assertEqual(models.Project.objects.count(), 3)

    def test_duplicate_name_shows_error(self):
        factories.ProjectFactory(name='dupe', user=alice)
        response = self.post_request(alice, {'name': 'dupe'})
        self.assertContains(response, escape(forms.DUPLICATE_PROJECT_ERROR))

    def test_name_contains_inlist_text_when_given_inlist_pk(self):
        item = factories.InlistItemFactory(user=alice)
        response = self.get_request(alice, inlistitem=item.pk)
        self.assertContains(response, item.text)
        self.assertEqual(response.context_data['form'].initial['name'],
            item)

    def test_deletes_inlist_item_when_given_inlist_pk(self):
        item = factories.InlistItemFactory(user=alice)
        response = self.post_request(alice, {'name': item.text},
            inlistitem=item.pk)
        self.assertEqual(models.InlistItem.objects.count(), 0)


class EditProjectViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/project_edit.html')

    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:edit_project',
            kwargs={'pk': self.project.pk})
        self.view = views.EditProjectView.as_view()

    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_uses_edit_project_form(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.EditProjectForm)

    def test_POST_request_edits_original_project(self):
        self.assertEqual(models.Project.objects.count(), 3)
        self.post_request(alice, {'name': 'updated', 'description': 'desc'},
            pk=self.project.pk)
        self.project.refresh_from_db()

        self.assertEqual(models.Project.objects.count(), 3)
        self.assertEqual(self.project.name, 'updated')
        self.assertEqual(self.project.description, 'desc')

    def test_POST_redirects_to_project_page(self):
        response = self.post_request(alice, pk=self.project.pk,
            data={'name': self.project.name,
                'description': self.project.description})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('projects:project', kwargs={'pk': self.project.pk}))

    def test_empty_name_saves_nothing_to_db(self):
        name = self.project.name
        self.post_request(alice, {'name': ''}, pk=self.project.pk)
        self.project.refresh_from_db()
        self.assertEqual(self.project.name, name)

    def test_empty_name_shows_error_on_page(self):
        response = self.post_request(alice, {'name': ''}, pk=self.project.pk)
        self.assertContains(response, forms.EMPTY_PROJECT_NAME_ERROR)

    def test_duplicate_name_saves_nothing_to_db(self):
        name = self.project.name
        p = factories.ProjectFactory(user=alice, name='dupe')

        self.post_request(alice, {'name': 'dupe'}, pk=self.project.pk)
        self.project.refresh_from_db()

        self.assertEqual(self.project.name, name)

    def test_duplicate_name_shows_error(self):
        p = factories.ProjectFactory(user=alice, name='dupe')
        response = self.post_request(alice, {'name': 'dupe'},
            pk=self.project.pk)
        self.assertContains(response, forms.DUPLICATE_PROJECT_ERROR)

    def test_returns_404_when_wrong_user_requests_page_with_get(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.project.pk)

    def test_returns_404_when_wrong_user_requests_page_with_post(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.project.pk)

    def test_returns_403_when_trying_to_edit_action_project_with_get(self):
        project = models.get_user_action_project(alice)
        response = self.get_request(alice, pk=project.pk)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_when_trying_to_edit_action_project_with_post(self):
        project = models.get_user_action_project(alice)
        response = self.post_request(alice, pk=project.pk)
        self.assertEqual(response.status_code, 403)

    @mock.patch('projects.views.permission_denied')
    def test_permission_denied_is_called_with_exception_argument(self,
        mock_permission_denied):
        project = models.get_user_action_project(alice)
        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request, self.url, pk=project.pk)

        mock_permission_denied.assert_called_once_with(request, None)


class DeleteProjectViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/project_confirm_delete.html')

    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:delete', kwargs={'pk': self.project.pk})
        self.view = views.DeleteProjectView.as_view()

    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser(), pk=self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_project_delete_view_shows_project_name(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertContains(response, self.project.name)

    def test_returns_404_when_wrong_user_requests_page_with_get(self):
        with self.assertRaises(Http404):
            self.get_request(bob, pk=self.project.pk)

    def test_returns_404_when_wrong_user_requests_page_with_post(self):
        with self.assertRaises(Http404):
            self.post_request(bob, pk=self.project.pk)

    def test_returns_403_when_deleting_users_action_project_with_get(self):
        response = self.get_request(alice,
            pk=models.get_user_action_project(alice).pk)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_when_deleting_users_action_project_with_post(self):
        response = self.post_request(alice,
            pk=models.get_user_action_project(alice).pk)
        self.assertEqual(response.status_code, 403)

    @mock.patch('projects.views.permission_denied')
    def test_403_error_gets_dummy_exception(self, mock_permission_denied):
        request = self.factory.post(self.url)
        request.user = alice
        self.view(request, self.url,
            pk=models.get_user_action_project(alice).pk)
        mock_permission_denied.assert_called_once_with(request, None)


class EditActionViewTests(ViewTestMixin, TestCase):
    templates = ('html.html', 'projects/base.html',
        'projects/edit_action.html')

    def setUp(self):
        self.action = factories.ActionlistItemFactory(user=alice)
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:edit_action', kwargs={'pk': self.action.pk})
        self.view = views.EditActionView.as_view()

    def test_uses_move_project_form(self):
        response = self.get_request(alice, pk=self.action.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.EditActionForm)

    def test_POST_request_updates_action(self):
        response = self.post_request(alice, {'project': self.project.pk,
            'text': self.action.text}, pk=self.action.pk)
        self.action.refresh_from_db()
        self.assertEqual(self.action.project, self.project)

    def test_POST_request_can_remove_project(self):
        self.action.project = self.project
        self.action.save()
        self.assertIsNotNone(self.action.project)

        response = self.post_request(alice,
            {'project': models.get_user_action_project(alice).pk,
            'text': self.action.text}, pk=self.action.pk)

        self.action.refresh_from_db()
        self.assertEqual(self.action.project,
            models.get_user_action_project(alice))

    def test_POST_that_moves_from_actionlist_returns_to_actionlist(self):
        self.assertEqual(self.action.project,
            models.get_user_action_project(alice))
        response = self.post_request(alice, {'project': self.project.pk,
            'text': self.action.text}, pk=self.action.pk)
        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': models.get_user_action_project(alice).pk}))

    def test_POST_that_moves_from_project_returns_to_same_project(self):
        self.action.project = self.project
        self.action.save()

        response = self.post_request(alice, {'text': self.action.text,
            'project': models.get_user_action_project(alice).pk},
            pk=self.action.pk)

        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': self.project.pk}))

    def test_POST_request_can_update_action_deadline(self):
        self.assertIsNone(self.action.deadline)
        self.post_request(alice, {'deadline_0': '1970-01-01',
            'deadline_1': '00:00:00', 'project': self.action.project.pk,
            'text': self.action.text}, pk=self.action.pk)
        self.action.refresh_from_db()
        self.assertEqual(str(self.action.deadline),
            '1970-01-01 00:00:00+00:00')

    def test_POST_request_can_update_action_text(self):
        self.post_request(alice, {'text': 'case of tests',
            'project': self.action.project.pk}, pk=self.action.pk)
        self.action.refresh_from_db()
        self.assertEqual(self.action.text, 'case of tests')

    def test_cannot_update_action_text_when_it_results_in_duplicate_text(self):
        action2 = factories.ActionlistItemFactory(user=alice)
        response = self.post_request(alice, {'text': self.action.text,
            'project': self.action.project.pk}, pk=action2.pk)
        self.assertContains(response, forms.DUPLICATE_MOVE_ERROR)
