# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase
import unittest

from projects.factories import ActionlistItemFactory
from projects.forms import (ActionlistForm, InlistForm, EMPTY_TEXT_ERROR,
    DUPLICATE_ITEM_ERROR)
from projects.models import InlistItem, ActionlistItem

User = get_user_model()

class InlistFormTest(unittest.TestCase):
    def test_inlist_form_placeholder_set(self):
        form = InlistForm()
        self.assertIn('placeholder="What needs to be done?"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = InlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_TEXT_ERROR])

    def test_form_crispy_helper(self):
        form = InlistForm()
        self.assertEqual(form.helper.form_method.lower(), 'post')
        self.assertIn('mui-form--inline', form.helper.form_class)


class InlistFormSlowTest(TestCase):
    def test_form_save(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        self.client.login(username='alice', password='alice')
        form = InlistForm(data={'text': 'test'})
        form.instance.user = alice

        form.is_valid()
        new_item = form.save(alice)

        self.assertEqual(InlistItem.objects.count(), 1)
        self.assertEqual(new_item, InlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        self.client.login(username='alice', password='alice')
        InlistItem.objects.create(text='dupe', user=alice)

        form = InlistForm(data={'text': 'dupe'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])


class ActionlistFormTest(unittest.TestCase):
    def test_actionlist_form_placeholder(self):
        form = ActionlistForm()
        self.assertIn('placeholder="What do you need to do?', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ActionlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_TEXT_ERROR])

    def test_form_crispy_helper(self):
        form = ActionlistForm()
        self.assertEqual(form.helper.form_method.lower(), 'post')
        self.assertIn('mui-form--inline', form.helper.form_class)

class ActionlistFormSlowTest(TestCase):
    def test_form_save(self):
        u = User.objects.create_user('alice', 'alice@test.org', 'alice')
        form = ActionlistForm(data={'text': 'test'})
        form.instance.user = u

        form.is_valid()
        new_item = form.save(u)

        self.assertEqual(ActionlistItem.objects.count(), 1)
        self.assertEqual(new_item, ActionlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        u = User.objects.create_user('alice', 'alice@test.org', 'alice')
        ActionlistItemFactory(text='dupe', user=u)

        form = ActionlistForm(data={'text': 'dupe'})
        form.instance.user = u

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [DUPLICATE_ITEM_ERROR])
