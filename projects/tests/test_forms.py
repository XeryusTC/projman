# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase
import unittest

from projects import factories, forms, models

User = get_user_model()

class InlistFormTest(unittest.TestCase):
    def test_inlist_form_placeholder_set(self):
        form = forms.InlistForm()
        self.assertIn('placeholder="What needs to be done?"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = forms.InlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.EMPTY_TEXT_ERROR])

    def test_form_crispy_helper(self):
        form = forms.InlistForm()
        self.assertEqual(form.helper.form_method.lower(), 'post')
        self.assertIn('mui-form--inline', form.helper.form_class)


class InlistFormSlowTest(TestCase):
    def test_form_save(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        form = forms.InlistForm(data={'text': 'test'})
        form.instance.user = alice

        form.is_valid()
        new_item = form.save(alice)

        self.assertEqual(models.InlistItem.objects.count(), 1)
        self.assertEqual(new_item, models.InlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        models.InlistItem.objects.create(text='dupe', user=alice)

        form = forms.InlistForm(data={'text': 'dupe'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.DUPLICATE_ITEM_ERROR])


class ActionlistFormTest(unittest.TestCase):
    def test_actionlist_form_placeholder(self):
        form = forms.ActionlistForm()
        self.assertIn('placeholder="What do you need to do?', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = forms.ActionlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.EMPTY_TEXT_ERROR])

    def test_form_crispy_helper(self):
        form = forms.ActionlistForm()
        self.assertEqual(form.helper.form_method.lower(), 'post')
        self.assertIn('mui-form--inline', form.helper.form_class)

class ActionlistFormSlowTest(TestCase):
    def test_form_save(self):
        u = User.objects.create_user('alice', 'alice@test.org', 'alice')
        form = forms.ActionlistForm(data={'text': 'test'})
        form.instance.user = u

        form.is_valid()
        new_item = form.save(u)

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEqual(new_item, models.ActionlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        u = User.objects.create_user('alice', 'alice@test.org', 'alice')
        factories.ActionlistItemFactory(text='dupe', user=u)

        form = forms.ActionlistForm(data={'text': 'dupe'})
        form.instance.user = u

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.DUPLICATE_ACTION_ERROR])
