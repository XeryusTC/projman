# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve, reverse
from django.http.response import Http404
from django.test import TestCase, RequestFactory
from django.utils.html import escape
import unittest
from unittest.mock import Mock, patch

from projects import factories, forms, models, views

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

class ViewTestCase(TestCase):
    factory = RequestFactory()

    def get_request(self, user, url=None, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.get(self.url)
        request.user = user
        return self.view(request, url, **kwargs)

    def post_request(self, user, data={}, url=None, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.post(self.url, data)
        request.user = user
        return self.view(request, url, **kwargs)


class TestMainPage(TestCase):
    def test_mainpage_url_resolves_to_mainpage_view(self):
        found = resolve(reverse('projects:main'))
        self.assertEqual(found.func.__name__,
            views.MainPageView.as_view().__name__)

    def test_mainpage_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get('/en/projects/')
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/mainpage.html')

    def test_login_required(self):
        response = self.client.get(reverse('projects:main'))
        self.assertRedirects(response,
            '/en/accounts/login/?next=/en/projects/')


class InlistpageTest(ViewTestCase):
    def setUp(self):
        self.url = '/en/projects/inlist/'
        self.view = views.InlistView.as_view()

    def test_inlist_url_resolves_to_inlist_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_inlist_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/inlist.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

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


class InlistItemDeleteViewTests(ViewTestCase):
    def setUp(self):
        self.item = factories.InlistItemFactory(user=alice)
        self.url = '/en/projects/inlist/{}/delete/'.format(self.item.pk)
        self.view = views.InlistItemDelete.as_view()

    def test_inlist_item_delete_view_is_delete_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_inlist_item_delete_view_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/inlistitem_confirm_delete.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser(), pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_inlist_item_delete_view_shows_item_name(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_returns_403_when_wrong_user_requests_page_with_get(self):
        response = self.get_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_when_wrong_user_requests_page_with_post(self):
        response = self.post_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)


class ActionlistViewTests(ViewTestCase):
    def setUp(self):
        self.url = '/en/projects/actions/'
        self.view = views.ActionlistView.as_view()

    def test_actionlist_url_resolves_to_actionlist_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_actionlist_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/actionlist.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_actionlist_uses_actionlist_form(self):
        response = self.get_request(alice)
        self.assertIsInstance(response.context_data['form'],
            forms.ActionlistForm)

    def test_actionlist_displays_only_items_for_that_user(self):
        item1 = factories.ActionlistItemFactory(text='item 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='item 2', user=alice)
        item3 = factories.ActionlistItemFactory(text='item 3', user=bob)

        response = self.get_request(alice)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_POST_request_saves_to_users_actionlist(self):
        response = self.post_request(alice, {'text': 'giants'})

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        item = models.ActionlistItem.objects.first()
        self.assertEqual(item.text, 'giants')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_actionlist(self):
        response = self.post_request(alice, {'text': 'test'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_empty_input_saves_nothing_to_db(self):
        response = self.post_request(alice, {'text': ''})
        self.assertEqual(models.ActionlistItem.objects.count(), 0)

    def test_empty_input_shows_error_on_page(self):
        response = self.post_request(alice, {'text': ''})
        self.assertContains(response, forms.EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_text_twice_shows_error_on_page(self):
        item1 = factories.ActionlistItemFactory(text='twice', user=alice)

        response = self.post_request(alice, {'text': 'twice'})

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertContains(response, forms.DUPLICATE_ACTION_ERROR)

    def test_context_includes_users_actionlist_items(self):
        item1 = factories.ActionlistItemFactory(text='action 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='action 2', user=alice)

        response = self.get_request(alice)

        self.assertIn('actionlist_items', response.context_data.keys())
        self.assertIn(item1, response.context_data['actionlist_items'])
        self.assertIn(item2, response.context_data['actionlist_items'])

    def test_only_uncompleted_items_in_context_actionlist(self):
        nc = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=False)
        co = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=True)

        response = self.get_request(alice)

        context = response.context_data['actionlist_items']
        self.assertEqual(len(nc), len(context))
        self.assertIn(nc[0], context)
        self.assertIn(nc[1], context)

    def test_context_includes_users_completed_action_list(self):
        item1 = factories.ActionlistItemFactory(user=alice, complete=True)
        item2 = factories.ActionlistItemFactory(user=alice, complete=True)

        response = self.get_request(alice)

        self.assertIn('actionlist_complete', response.context_data.keys())
        self.assertIn(item1, response.context_data['actionlist_complete'])
        self.assertIn(item2, response.context_data['actionlist_complete'])

    def test_only_completed_items_in_context_actionlist_complete(self):
        nc = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=False)
        co = factories.ActionlistItemFactory.create_batch(2, user=alice,
            complete=True)

        response = self.get_request(alice)

        context = response.context_data['actionlist_complete']
        self.assertEqual(len(co), len(context))
        self.assertIn(co[0], context)
        self.assertIn(co[1], context)

    def test_only_show_action_items_without_project(self):
        project = factories.ProjectFactory(user=alice)
        item1 = factories.ActionlistItemFactory(user=alice)
        item2 = factories.ActionlistItemFactory(user=alice, project=project)

        response = self.get_request(alice)

        actionlist = response.context_data['actionlist_items']
        self.assertIn(item1, actionlist)
        self.assertNotIn(item2, actionlist)
        self.assertSequenceEqual([],
            response.context_data['actionlist_complete'])


class ActionlistItemDeleteViewTests(ViewTestCase):
    def setUp(self):
        self.item = factories.ActionlistItemFactory(user=alice)
        self.url = '/en/projects/actions/{}/delete/'.format(self.item.pk)
        self.view = views.ActionlistItemDelete.as_view()

    def test_actionlist_item_delete_view_is_delete_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__,
            views.ActionlistItemDelete.as_view().__name__)

    def test_actionlist_item_delete_view_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/actionlistitem_confirm_delete.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser(), pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_actionlist_item_delete_view_shows_item_text(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_POST_redirects_to_action_list_for_non_project_actions(self):
        response = self.post_request(alice, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:actionlist'))

    def test_POST_redirects_to_project_page_for_project_actions(self):
        project = factories.ProjectFactory(user=alice)
        item = factories.ActionlistItemFactory(user=alice, project=project)
        response = self.post_request(alice, pk=item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:project',
            kwargs={'pk': project.pk}))

    def test_GET_from_different_user_shows_403_Forbidden(self):
        response = self.get_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)

    def test_POST_from_different_user_shows_403_Forbidden(self):
        response = self.post_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)


class ActionCompleteViewTest(ViewTestCase):
    def setUp(self):
        self.item = factories.ActionlistItemFactory(user=alice)
        self.url = reverse('projects:complete_action',
            kwargs={'pk': self.item.pk})
        self.view = views.ActionCompleteView.as_view()

    def test_complete_action_view_is_complete_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_actioncomple_can_fall_back_to_correct_template(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get('/en/projects/actions/0/complete/')
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/actionlistitem_errorform.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('account_login') + '?next=' + self.url)

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
        self.assertEqual(response.url, reverse('projects:actionlist'))

    def test_redirects_to_project_page_when_action_has_project(self):
        project = factories.ProjectFactory(user=alice)
        item = factories.ActionlistItemFactory(user=alice, project=project)
        response = self.post_request(alice, pk=item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('projects:project', kwargs={'pk': project.pk}))


class ConvertInlistItemToActionItemTest(ViewTestCase):
    def setUp(self):
        self.item = factories.InlistItemFactory(user=alice)
        self.url = reverse('projects:convert_inlist_action',
            kwargs={'pk': self.item.pk})
        self.view = views.InlistItemToActionView.as_view()

    def test_convert_inlist_to_action_is_correct_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_convert_to_action_view_usses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/convert_inlist_to_action.html')

    def test_uses_correct_form_class(self):
        response = self.get_request(alice, pk=self.item.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.ConvertInlistToActionForm)

    def test_login_required(self):
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

    def test_get_request_from_wrong_user_returns_403_Forbidden(self):
        response = self.get_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)

    def test_post_request_from_wrong_user_returns_403_Forbidden(self):
        response = self.post_request(bob, pk=self.item.pk)
        self.assertEqual(response.status_code, 403)


class ProjectViewTests(ViewTestCase):
    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:project', kwargs={'pk':self.project.pk})
        self.view = views.ProjectView.as_view()

    def test_project_url_resolves_to_project_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_project_page_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/project.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
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


class CreateProjectViewTests(ViewTestCase):
    def setUp(self):
        self.url = reverse('projects:create_project')
        self.view = views.CreateProjectView.as_view()

    def test_create_project_url_resolves_to_create_project_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_create_project_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/create_project.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_uses_create_project_form(self):
        response = self.get_request(alice)
        self.assertIsInstance(response.context_data['form'],
            forms.CreateProjectForm)

    def test_POST_request_saves_to_user(self):
        response = self.post_request(alice, {'name': 'Watch videos'})
        self.assertEqual(models.Project.objects.count(), 1)
        item = models.Project.objects.first()
        self.assertEqual(item.name, 'Watch videos')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_project_page(self):
        response = self.post_request(alice, {'name': 'Watch videos'})
        project = models.Project.objects.first()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url,
            reverse('projects:project', kwargs={'pk':project.pk}))

    def test_empty_name_saves_nothing_to_db(self):
        response = self.post_request(alice, {'name': ''})
        self.assertEqual(models.Project.objects.count(), 0)

    def test_empty_name_shows_error_on_page(self):
        response = self.post_request(alice, {'name': ''})
        self.assertContains(response, forms.EMPTY_PROJECT_NAME_ERROR)

    def test_duplicate_name_saves_nothing_to_db(self):
        factories.ProjectFactory(name='dupe', user=alice)
        response = self.post_request(alice, {'name': 'dupe'})
        self.assertEqual(models.Project.objects.count(), 1)

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


class EditProjectViewTests(ViewTestCase):
    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:edit_project',
            kwargs={'pk': self.project.pk})
        self.view = views.EditProjectView.as_view()

    def test_edit_project_url_resovles_to_edit_project_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_edit_project_page_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url, kwargs={'pk': self.project.pk})
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/project_edit.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_uses_edit_project_form(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertIsInstance(response.context_data['form'],
            forms.EditProjectForm)

    def test_POST_request_edits_original_project(self):
        self.assertEqual(models.Project.objects.count(), 1)
        self.post_request(alice, {'name': 'updated', 'description': 'desc'},
            pk=self.project.pk)
        self.project.refresh_from_db()

        self.assertEqual(models.Project.objects.count(), 1)
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


class DeleteProjectViewTests(ViewTestCase):
    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)
        self.url = reverse('projects:delete', kwargs={'pk': self.project.pk})
        self.view = views.DeleteProjectView.as_view()

    def test_inlist_item_delete_url_resolves_to_correct_delete_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_inlist_item_delete_view_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/project_confirm_delete.html')

    def test_login_required(self):
        response = self.get_request(AnonymousUser(), pk=self.project.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_project_delete_view_shows_project_name(self):
        response = self.get_request(alice, pk=self.project.pk)
        self.assertContains(response, self.project.name)

    def test_returns_403_when_wrong_user_requests_page_with_get(self):
        response = self.get_request(bob, pk=self.project.pk)
        self.assertEqual(response.status_code, 403)

    def test_returns_403_when_wrong_user_requests_page_with_post(self):
        response = self.post_request(bob, pk=self.project.pk)
        self.assertEqual(response.status_code, 403)
