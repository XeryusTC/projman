# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from django.test import TestCase

from settings import models

User = get_user_model()
alice = None

def setUpModule():
    global alice
    alice = User.objects.create_user('alice', 'alice@test.org', 'alice')

def tearDownModule():
    alice.delete()

def reset_user_settings(settings):
    settings.language = 'en-us'
    settings.inlist_delete_confirm = True
    settings.action_delete_confirm = True

class SettingsTests(TestCase):
    def setUp(self):
        reset_user_settings(alice.settings)

    def test_settings_has_user_field(self):
        models.Settings.objects.get(user=alice)

    def test_user_can_have_only_one_set_of_settings(self):
        with self.assertRaises(IntegrityError):
            duplicate = models.Settings.objects.create(user=alice)

    def test_user_reverse_relation_has_correct_name(self):
        # the related_name should be set to settings
        self.assertIsInstance(models.Settings.objects.get(user=alice),
            models.Settings)

    def test_settings_has_language_field(self):
        alice.settings.language

    def test_settings_has_inlist_delete_confirm_field(self):
        alice.settings.inlist_delete_confirm

    def test_inlist_delete_confirm_field_is_true_by_default(self):
        self.assertTrue(alice.settings.inlist_delete_confirm)

    def test_inlist_delete_confirm_field_can_be_false(self):
        alice.settings.inlist_delete_confirm = False
        alice.settings.save()

    def test_action_delete_confirm_is_true_by_default(self):
        self.assertTrue(alice.settings.inlist_delete_confirm)

    def test_action_delete_confirm_can_be_false(self):
        alice.settings.action_delete_confirm = False
        alice.settings.save()

    def test_string_representation(self):
        self.assertEqual(str(alice.settings), "alice's settings")
