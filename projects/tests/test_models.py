# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from projects import factories
from projects.models import InlistItem, ActionlistItem, Project

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

    def test_has_complete_field(self):
        item = ActionlistItem(text='test', user=u, complete=False)
        item.save()

    def test_complete_field_defaults_to_false(self):
        item = factories.ActionlistItemFactory(user=u)
        item.save()
        self.assertFalse(item.complete)

    def test_has_project_field(self):
        project = factories.ProjectFactory(user=u)
        item = ActionlistItem(text='test', user=u, project=project)
        item.save()

    def test_project_field_refers_to_no_project_by_default(self):
        item = factories.ActionlistItemFactory(user=u)
        item.save()
        self.assertIsNone(item.project)

    def test_action_user_and_project_user_should_be_equal(self):
        bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
        project = factories.ProjectFactory(user=bob)

        item = ActionlistItem(text='test', user=u, project=project)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_related_field_has_sensible_name(self):
        project = factories.ProjectFactory(user=u)
        item = factories.ActionlistItemFactory(user=u, project=project)
        self.assertSequenceEqual(project.action_list.all(), [item])

    def test_can_have_same_action_text_on_actionlist_and_project(self):
        project = factories.ProjectFactory(user=u)
        item1 = factories.ActionlistItemFactory(user=u, text='not dupe')
        item2 = factories.ActionlistItemFactory(user=u, text='not dupe',
            project=project)

    def test_can_have_same_action_text_on_different_projects(self):
        projects = factories.ProjectFactory.create_batch(user=u, size=2)
        item1 = factories.ActionlistItemFactory(user=u, text='not dupe',
            project=projects[0])
        item2 = factories.ActionlistItemFactory(user=u, text='not dupe',
            project=projects[1])


class ProjectModelTests(TestCase):
    def test_default_name(self):
        item = Project()
        self.assertEqual(item.name, '')

    def test_user_required(self):
        item = factories.ProjectFactory(user=u)

    def test_cannot_save_projects_without_a_name(self):
        item = factories.ProjectFactory(name='', user=u)
        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_user_cannot_have_duplicate_projects(self):
        factories.ProjectFactory(name='dupe', user=u)
        with self.assertRaises(ValidationError):
            item = Project(name='dupe', user=u)
            item.full_clean()

    def test_different_users_can_have_the_same_project(self):
        bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
        factories.ProjectFactory(name='build website', user=u)
        item = factories.ProjectFactory(name='build website', user=bob)
        item.full_clean()

    def test_can_have_description(self):
        item = factories.ProjectFactory(user=u, name='test',
            description='desc')

    def test_description_is_not_required(self):
        item = factories.ProjectFactory(user=u, name='test', description='')
        item.full_clean()

    def test_string_representation(self):
        item1 = factories.ProjectFactory(name='test project', user=u)
        item2 = factories.ProjectFactory(name='second project', user=u)
        self.assertEqual(str(item1), 'test project')
        self.assertEqual(str(item2), 'second project')
