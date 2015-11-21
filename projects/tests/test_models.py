# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from projects import factories
from projects.models import InlistItem, ActionlistItem

User = get_user_model()
u = None

def setUpModule():
    global u
    u = User.objects.create_user('alice', 'alice@test.org', 'alice')

def tearDownModule():
    u.delete()

class InlistItemModelTest(TestCase):
    def test_default_text(self):
        item = InlistItem()
        self.assertEqual(item.text, '')

    def test_user_required(self):
        item = factories.InlistItemFactory(user=u)

    def test_cannot_save_empty_inlist_items(self):
        item = factories.InlistItemFactory(text='', user=u)
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        factories.InlistItemFactory(text='dupe', user=u)
        with self.assertRaises(ValidationError):
            item = InlistItem(text='dupe', user=u)
            item.full_clean()

    def test_can_different_users_can_have_same_items(self):
        bob = User.objects.create_user('bob', 'bob@test.com', 'bob')
        factories.InlistItemFactory(text='not dupe', user=u)
        item = factories.InlistItemFactory(text='not dupe', user=bob)
        item.full_clean() # should not raise ValidationError

    def test_string_representation(self):
        item = factories.InlistItemFactory(text='test item', user=u)
        self.assertEqual(str(item), 'test item')


class ActionlistItemModelTest(TestCase):
    def test_default_text(self):
        item = ActionlistItem()
        self.assertEqual(item.text, '')

    def test_user_required(self):
        item = factories.ActionlistItemFactory(user=u)

    def test_cannot_save_empty_actionlist_item(self):
        item = factories.ActionlistItemFactory(text='', user=u)
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_actionlist_items_are_invalid(self):
        factories.ActionlistItemFactory(text='double', user=u)
        with self.assertRaises(ValidationError):
            item = ActionlistItem(text='double', user=u)
            item.full_clean()

    def test_different_users_can_have_same_items(self):
        bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
        factories.ActionlistItemFactory(text='pass test', user=u)
        item = factories.ActionlistItemFactory(text='pass test', user=bob)
        item.full_clean()

    def test_string_representation(self):
        item1 = factories.ActionlistItemFactory(text='test item', user=u)
        item2 = factories.ActionlistItemFactory(text='other item', user=u)
        self.assertEqual(str(item1), 'test item')
        self.assertEqual(str(item2), 'other item')
