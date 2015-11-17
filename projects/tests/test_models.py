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

    def test_string_representation(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        item = InlistItemFactory(text='test item', user=alice)
        self.assertEqual(str(item), 'test item')
