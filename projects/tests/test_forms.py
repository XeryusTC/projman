# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.test import TestCase
import unittest

from projects.forms import InlistForm, EMPTY_TEXT_ERROR
from projects.models import InlistItem

User = get_user_model()

class InlistFormTest(unittest.TestCase):
    def test_inlist_form_placeholder_set(self):
        form = InlistForm()
        self.assertIn('placeholder="What needs to be done?"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = InlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [EMPTY_TEXT_ERROR])


class InlistFormSlowTest(TestCase):
    def test_form_save(self):
        alice = User.objects.create_user('alice', 'alice@test.com', 'alice')
        self.client.login(username='alice', password='alice')
        form = InlistForm(data={'text': 'test'})

        form.is_valid()
        new_item = form.save(alice)
        new_item.save()

        self.assertEqual(InlistItem.objects.count(), 1)
        self.assertEqual(new_item, InlistItem.objects.first())
