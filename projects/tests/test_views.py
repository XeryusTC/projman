# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
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
    @classmethod
    def setUpClass(cls):
        super(InlistpageTest, cls).setUpClass()
        cls.alice = alice
        cls.bob = bob

    def setUp(self):
        self.client.login(username='alice', password='alice')
        self.url = reverse('projects:inlist')

    def test_inlist_url_resolves_to_inlist_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__,
            views.InlistView.as_view().__name__)

    def test_inlist_uses_correct_templates(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/inlist.html')

    def test_inlist_uses_inlist_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], InlistForm)

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response,
            '/en/accounts/login/?next=/en/projects/inlist/')

    def test_displays_only_items_for_that_user(self):
        item1 = factories.InlistItemFactory(text='item 1', user=self.alice)
        item2 = factories.InlistItemFactory(text='item 2', user=self.alice)
        item3 = factories.InlistItemFactory(text='item 3', user=self.bob)

        response = self.client.get(self.url)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_saves_POST_request_to_the_users_inlist(self):
        self.client.post(self.url, data={'text': 'ecila'})

        self.assertEqual(InlistItem.objects.count(), 1)
        item = InlistItem.objects.first()
        self.assertEqual(item.text, 'ecila')
        self.assertEqual(item.user, self.alice)

    def test_POST_redirects_to_inlist_page(self):
        response = self.client.post('/en/projects/inlist/',
            data={'text': 'test'})
        self.assertRedirects(response, '/en/projects/inlist/')

    def test_invalid_input_saves_nothing_to_db(self):
        response = self.client.post(self.url, data={'text': ''})
        self.assertEqual(InlistItem.objects.count(), 0)

    def test_context_variables_contains_users_inlist_items(self):
        item1 = factories.InlistItemFactory(text='item 1', user=self.alice)
        item2 = factories.InlistItemFactory(text='item 2', user=self.alice)

        response = self.client.get(self.url)

        self.assertIn('inlist_items', response.context.keys())
        self.assertIn(item1, response.context['inlist_items'])
        self.assertIn(item2, response.context['inlist_items'])

    def test_form_invalid_input_shows_error_on_page(self):
        response = self.client.post(self.url, data={'text': ''})

        self.assertFalse(InlistItem.objects.count(), 0)
        self.assertContains(response, EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_item_twice_shows_error_on_page(self):
        item1 = factories.InlistItemFactory(text='dupe', user=self.alice)

        response = self.client.post(self.url, data={'text': 'dupe'})

        self.assertEqual(InlistItem.objects.count(), 1)
        self.assertContains(response, escape(DUPLICATE_ITEM_ERROR))


class InlistItemDeleteViewTests(TestCase):
    def setUp(self):
        self.alice = alice
        self.client.login(username='alice', password='alice')
        self.item = factories.InlistItemFactory(user=self.alice)

    def test_inlist_item_delete_view_is_delete_view(self):
        found = resolve(reverse('projects:delete_inlist',
            kwargs={'pk': 0}))
        self.assertEqual(found.func.__name__,
            views.InlistItemDelete.as_view().__name__)

    def test_inlist_item_delete_view_uses_correct_templates(self):
        # For some reason reverse doesn't work, so we have to construct
        # the url ourselves
        response = self.client.get('/en/projects/inlist/{}/delete/'.format(
            self.item.pk))
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response,
            'projects/inlistitem_confirm_delete.html')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get('/en/projects/inlist/0/delete/')
        self.assertRedirects(response,
            '/en/accounts/login/?next=/en/projects/inlist/0/delete/')

    def test_inlist_item_delete_view_shows_item_name(self):
        response = self.client.get('/en/projects/inlist/{}/delete/'.format(
            self.item.pk))
        self.assertContains(response, self.item.text)


class ActionlistViewTests(TestCase):
    def setUp(self):
        self.url = reverse('projects:actionlist')
        self.client.login(username='alice', password='alice')

    def test_actionlist_url_resolves_to_actionlist_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__,
            views.ActionlistView.as_view().__name__)

    def test_actionlist_uses_correct_templates(self):
        self.client.login(username='alice', password='alice')
        response = self.client.get('/en/projects/actions/')
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'projects/base.html')
        self.assertTemplateUsed(response, 'projects/actionlist.html')

    def test_login_required(self):
        self.client.logout()
        response = self.client.get(reverse('projects:actionlist'))
        self.assertRedirects(response,
        '/en/accounts/login/?next=/en/projects/actions/')

    def test_actionlist_uses_actionlist_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], ActionlistForm)

    def test_actionlist_displays_only_items_for_that_user(self):
        item1 = factories.ActionlistItemFactory(text='item 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='item 2', user=alice)
        item3 = factories.ActionlistItemFactory(text='item 3', user=bob)

        response = self.client.get(self.url)

        self.assertContains(response, 'item 1')
        self.assertContains(response, 'item 2')
        self.assertNotContains(response, 'item 3')

    def test_POST_request_saves_to_users_actionlist(self):
        self.client.post(self.url, data={'text': 'giants'})

        self.assertEqual(ActionlistItem.objects.count(), 1)
        item = ActionlistItem.objects.first()
        self.assertEqual(item.text, 'giants')
        self.assertEqual(item.user, alice)

    def test_POST_redirects_to_actionlist(self):
        response = self.client.post('/en/projects/actions/', data={'text': 'test'})
        self.assertRedirects(response, '/en/projects/actions/')

    def test_empty_input_saves_nothing_to_db(self):
        response = self.client.post(self.url, data={'text': ''})
        self.assertEqual(ActionlistItem.objects.count(), 0)

    def test_empty_input_shows_error_on_page(self):
        response = self.client.post(self.url, data={'text': ''})

        self.assertEqual(ActionlistItem.objects.count(), 0)
        self.assertContains(response, EMPTY_TEXT_ERROR)

    def test_trying_to_enter_same_text_twice_shows_error_on_page(self):
        item1 = factories.ActionlistItemFactory(text='twice', user=alice)

        response = self.client.post(self.url, data={'text': 'twice'})

        self.assertEqual(ActionlistItem.objects.count(), 1)
        self.assertContains(response, escape(DUPLICATE_ACTION_ERROR))

    def test_context_includes_users_actionlist_items(self):
        item1 = factories.ActionlistItemFactory(text='action 1', user=alice)
        item2 = factories.ActionlistItemFactory(text='action 2', user=alice)

        response = self.client.get(self.url)

        self.assertIn('actionlist_items', response.context.keys())
        self.assertIn(item1, response.context['actionlist_items'])
        self.assertIn(item2, response.context['actionlist_items'])
