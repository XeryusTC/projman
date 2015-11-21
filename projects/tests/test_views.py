# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase, RequestFactory
from django.utils.html import escape
import unittest
from unittest.mock import Mock, patch

from projects import factories, views
from projects.forms import (ActionlistForm, InlistForm, EMPTY_TEXT_ERROR,
        DUPLICATE_ITEM_ERROR, DUPLICATE_ACTION_ERROR)
from projects.models import InlistItem, ActionlistItem

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


class InlistpageTest(TestCase):
    def setUp(self):
        self.url = '/en/projects/inlist/'
        self.factory = RequestFactory()
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
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_inlist_uses_inlist_form(self):
        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)
        self.assertIsInstance(response.context_data['form'], InlistForm)

    def test_displays_only_items_for_that_user(self):
        item1 = factories.InlistItemFactory(text='item 1', user=alice)
        item2 = factories.InlistItemFactory(text='item 2', user=alice)
        item3 = factories.InlistItemFactory(text='item 3', user=bob)

        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_saves_POST_request_to_the_users_inlist(self):
        request = self.factory.post(self.url, {'text': 'ecila'})
        request.user = alice
        response = self.view(request)

        self.assertEqual(InlistItem.objects.count(), 1)
        item = InlistItem.objects.first()
        self.assertEqual(item.text, 'ecila')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_inlist_page(self):
        request = self.factory.post(self.url, {'text': 'test'})
        request.user = alice
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_invalid_input_saves_nothing_to_db(self):
        request = self.factory.post(self.url, {'text': ''})
        request.user = alice
        response = self.view(request)
        self.assertEqual(InlistItem.objects.count(), 0)

    def test_context_variable_contains_users_inlist_items(self):
        item1 = factories.InlistItemFactory(text='item 1', user=alice)
        item2 = factories.InlistItemFactory(text='item 2', user=alice)

        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)

        self.assertIn('inlist_items', response.context_data.keys())
        self.assertIn(item1, response.context_data['inlist_items'])
        self.assertIn(item2, response.context_data['inlist_items'])

    def test_form_invalid_input_shows_error_on_page(self):
        request = self.factory.post(self.url, {'text': ''})
        request.user = alice
        response = self.view(request)

        self.assertEqual(InlistItem.objects.count(), 0)
        self.assertContains(response, EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_item_twice_shows_error_on_page(self):
        item1 = factories.InlistItemFactory(text='dupe', user=alice)

        request = self.factory.post(self.url, {'text': 'dupe'})
        request.user = alice
        response = self.view(request)

        self.assertEqual(InlistItem.objects.count(), 1)
        self.assertContains(response, escape(DUPLICATE_ITEM_ERROR))


class InlistItemDeleteViewTests(TestCase):
    def setUp(self):
        self.item = factories.InlistItemFactory(user=alice)
        self.factory = RequestFactory()
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
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = self.view(request, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_inlist_item_delete_view_shows_item_name(self):
        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request, pk=self.item.pk)
        self.assertContains(response, self.item.text)


class ActionlistViewTests(TestCase):
    def setUp(self):
        self.url = '/en/projects/actions/'
        self.view = views.ActionlistView.as_view()
        self.factory = RequestFactory()

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
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_actionlist_uses_actionlist_form(self):
        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)
        self.assertIsInstance(response.context_data['form'], ActionlistForm)

    def test_actionlist_displays_only_items_for_that_user(self):
        item1 = factories.ActionlistItemFactory(text='item 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='item 2', user=alice)
        item3 = factories.ActionlistItemFactory(text='item 3', user=bob)

        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_POST_request_saves_to_users_actionlist(self):
        request = self.factory.post(self.url, {'text': 'giants'})
        request.user = alice

        response = self.view(request)

        self.assertEqual(ActionlistItem.objects.count(), 1)
        item = ActionlistItem.objects.first()
        self.assertEqual(item.text, 'giants')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_actionlist(self):
        request = self.factory.post(self.url, {'text': 'test'})
        request.user = alice
        response = self.view(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, self.url)

    def test_empty_input_saves_nothing_to_db(self):
        request = self.factory.post(self.url, {'text': ''})
        request.user = alice
        response = self.view(request)
        self.assertEqual(ActionlistItem.objects.count(), 0)

    def test_empty_input_shows_error_on_page(self):
        request = self.factory.post(self.url, {'text': ''})
        request.user = alice
        response = self.view(request)
        self.assertContains(response, EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_text_twice_shows_error_on_page(self):
        item1 = factories.ActionlistItemFactory(text='twice', user=alice)

        request = self.factory.post(self.url, {'text': 'twice'})
        request.user = alice
        response = self.view(request)

        self.assertEqual(ActionlistItem.objects.count(), 1)
        self.assertContains(response, DUPLICATE_ACTION_ERROR)

    def test_context_includes_users_actionlist_items(self):
        item1 = factories.ActionlistItemFactory(text='action 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='action 2', user=alice)

        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request)

        self.assertIn('actionlist_items', response.context_data.keys())
        self.assertIn(item1, response.context_data['actionlist_items'])
        self.assertIn(item2, response.context_data['actionlist_items'])


class ActionlistItemDeleteViewTests(TestCase):
    def setUp(self):
        self.item = factories.ActionlistItemFactory(user=alice)
        self.url = '/en/projects/actions/{}/delete/'.format(self.item.pk)
        self.factory = RequestFactory()
        self.view = views.ActionlistItemDelete.as_view()

    def test_inlist_item_delete_view_is_delete_view(self):
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
        request = self.factory.get(self.url)
        request.user = AnonymousUser()
        response = self.view(request, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/en/accounts/login/?next=' + self.url)

    def test_actionlist_item_delete_view_shows_item_text(self):
        request = self.factory.get(self.url)
        request.user = alice
        response = self.view(request, pk=self.item.pk)
        self.assertContains(response, self.item.text)

    def test_POST_redirects_to_action_list(self):
        request = self.factory.post(self.url)
        request.user = alice
        response = self.view(request, pk=self.item.pk)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('projects:actionlist'))
