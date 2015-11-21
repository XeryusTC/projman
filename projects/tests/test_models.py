# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from projects import factories
from projects.models import InlistItem

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
