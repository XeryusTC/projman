# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.urlresolvers import resolve, reverse
from django.test import TestCase
import unittest
from unittest.mock import Mock, patch

from project import factories, views
from project.forms import InlistForm
from project.models import InlistItem

User = get_user_model()

class TestMainPage(TestCase):
    def test_mainpage_url_resolves_to_mainpage_view(self):
        found = resolve(reverse('project:main'))
        self.assertEqual(found.func.__name__,
            views.MainPageView.as_view().__name__)

    def test_mainpage_uses_correct_templates(self):
        response = self.client.get('/en/project/')
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'project/base.html')
        self.assertTemplateUsed(response, 'project/mainpage.html')


class InlistpageTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', 'alice@test.com',
            'alice')
        self.bob = User.objects.create_user('bob', 'bob@test.com', 'bob')
        self.client.login(username='alice', password='alice')
        self.url = reverse('project:inlist')

    def test_inlist_url_resolves_to_inlist_view(self):
        found = resolve(reverse('project:inlist'))
        self.assertEqual(found.func.__name__,
            views.InlistView.as_view().__name__)

    def test_inlist_uses_correct_templates(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'html.html')
        self.assertTemplateUsed(response, 'project/base.html')
        self.assertTemplateUsed(response, 'project/inlist.html')

    def test_inlist_uses_inlist_form(self):
        response = self.client.get(self.url)
        self.assertIsInstance(response.context['form'], InlistForm)

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
        response = self.client.post('/en/project/inlist/',
            data={'text': 'test'})
        self.assertRedirects(response, '/en/project/inlist/')

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
        self.fail('Implement test')
