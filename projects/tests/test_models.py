# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from projects.factories import InlistItemFactory
from projects.models import InlistItem

User = get_user_model()

class InlistItemModelTest(TestCase):
    def test_default_text(self):
        item = InlistItem()
        self.assertEqual(item.text, '')

    def test_user_required(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        item = InlistItemFactory(user=alice)

    def test_cannot_save_empty_inlist_items(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        item = InlistItemFactory(text='', user=alice)
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        InlistItemFactory(text='dupe', user=alice)
        with self.assertRaises(ValidationError):
            item = InlistItem(text='dupe', user=alice)
            item.full_clean()

    def test_can_different_users_can_have_same_items(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        bob = User.objects.create_user('bob', 'bob@test.com', 'bob')
        InlistItemFactory(text='not dupe', user=alice)
        item = InlistItemFactory(text='not dupe', user=bob)
        item.full_clean() # should not raise ValidationError

    def test_string_representation(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        item = InlistItemFactory(text='test item', user=alice)
        self.assertEqual(str(item), 'test item')
