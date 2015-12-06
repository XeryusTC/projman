# -*- coding: utf-8 -*-
from django.core.exceptions import NON_FIELD_ERRORS
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


class CompleteActionFormTest(TestCase):
    def test_form_save(self):
        alice = User.objects.create_user('alice', 'alice@test.org', 'alice')
        item = factories.ActionlistItemFactory(user=alice)
        form = forms.CompleteActionForm()

        form.save(item, alice)

        self.assertTrue(item.complete)

    def test_form_invalid_for_wrong_user(self):
        alice = User.objects.create_user('alice', 'alice@test.org', 'alice')
        trudy = User.objects.create_user('trudy', 'trudy@test.org', 'trudy')
        item = factories.ActionlistItemFactory(user=alice)
        form = forms.CompleteActionForm()

        form.is_valid()
        form.save(item, trudy)

        self.assertFalse(item.complete)
        self.assertEqual(form.errors[NON_FIELD_ERRORS], [forms.ILLEGAL_ACTION_ERROR])

    def test_form_toggles_true_to_false(self):
        alice = User.objects.create_user('alice', 'alice@test.org', 'alice')
        item = factories.ActionlistItemFactory(user=alice, complete=True)
        form = forms.CompleteActionForm()

        form.save(item, alice)

        self.assertFalse(item.complete)


class ConvertInlistToActionFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alice', 'alice@test.org', 'alice')

    def test_form_save_creates_action_item(self):
        item = factories.InlistItemFactory(user=self.user)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})
        self.assertEqual(models.ActionlistItem.objects.count(), 0)

        form.is_valid()
        form.save(item, self.user)

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEqual(models.ActionlistItem.objects.first().text,
            item.text)

    def test_form_save_deletes_inlist_item(self):
        item = factories.InlistItemFactory(user=self.user)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})
        self.assertEqual(models.InlistItem.objects.count(), 1)

        form.is_valid()
        form.save(item, self.user)

        self.assertEqual(models.InlistItem.objects.count(), 0)

    def test_form_invalid_for_wrong_user(self):
        trudy = User.objects.create_user('trudy', 'trudy@test.org', 'trudy')
        item = factories.InlistItemFactory(user=self.user)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        form.is_valid()
        form.save(item, trudy)

        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [forms.ILLEGAL_ACTION_ERROR])

    def test_form_invalid_for_duplicate_action_text(self):
        factories.ActionlistItemFactory(user=self.user, text='duplicate')
        item = factories.InlistItemFactory(user=self.user, text='duplicate')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        form.is_valid()
        form.save(item, self.user)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.DUPLICATE_ACTION_ERROR])
        self.assertEqual(models.ActionlistItem.objects.count(), 1)

    def test_form_valid_for_duplicate_action_text_for_other_user(self):
        bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
        factories.ActionlistItemFactory(user=bob, text='not dupe')
        item = factories.InlistItemFactory(user=self.user, text='not dupe')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        form.is_valid()
        form.save(item, self.user)

        self.assertTrue(form.is_valid())
        self.assertEqual(models.ActionlistItem.objects.count(), 2)

    def test_form_invalid_for_empty_text(self):
        item = factories.InlistItemFactory(user=self.user, text='')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.EMPTY_TEXT_ERROR])
