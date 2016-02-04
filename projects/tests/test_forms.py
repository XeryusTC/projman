# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth import get_user_model
from django.test import TestCase

from projects import factories, forms, models

User = get_user_model()
alice = None
bob = None
trudy = None

def setUpModule():
    global alice, bob, trudy
    alice = User.objects.create_user('alice', 'alice@test.org', 'alice')
    bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
    trudy = User.objects.create_user('trudy', 'trudy@test.org', 'trudy')

def tearDownModule():
    alice.delete()
    bob.delete()
    trudy.delete()

class InlistFormTest(TestCase):
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

    def test_form_saves_to_db(self):
        form = forms.InlistForm(data={'text': 'test'})
        form.instance.user = alice

        form.is_valid()
        new_item = form.save(alice)

        self.assertEqual(models.InlistItem.objects.count(), 1)
        self.assertEqual(new_item, models.InlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        models.InlistItem.objects.create(text='dupe', user=alice)
        form = forms.InlistForm(data={'text': 'dupe'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.DUPLICATE_ITEM_ERROR])


class ActionlistFormTest(TestCase):
    def test_actionlist_form_placeholder(self):
        form = forms.ActionlistForm()
        self.assertIn('placeholder="What do you need to do?', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = forms.ActionlistForm(data={'text': ''})
        form.instance.user = alice
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.EMPTY_TEXT_ERROR])

    def test_form_crispy_helper(self):
        form = forms.ActionlistForm()
        self.assertEqual(form.helper.form_method.lower(), 'post')
        self.assertIn('mui-form--inline', form.helper.form_class)

    def test_form_save(self):
        form = forms.ActionlistForm(data={'text': 'test'})
        form.instance.user = alice

        form.is_valid()
        new_item = form.save()

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEqual(new_item, models.ActionlistItem.objects.first())

    def test_form_validation_for_duplicate_items(self):
        factories.ActionlistItemFactory(text='dupe', user=alice)

        form = forms.ActionlistForm(data={'text': 'dupe'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [forms.DUPLICATE_ACTION_ERROR])

    def test_form_defaults_save_to_no_project(self):
        form = forms.ActionlistForm(data={'text': 'test'})
        form.instance.user = alice

        form.is_valid()
        item = form.save()

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEqual(item.project, models.Project.objects.get(user=alice,
            name=models.ACTION_PROJECT_NAME))

    def test_form_can_save_action_to_project(self):
        p = factories.ProjectFactory(user=alice)
        form = forms.ActionlistForm(data={'text': 'test'})
        form.instance.user = alice
        form.instance.project = p

        form.is_valid()
        item = form.save()

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEquals(item.project, p)

    def test_cannot_save_action_to_project_which_doesnt_belong_to_user(self):
        p = factories.ProjectFactory(user=bob)

        form = forms.ActionlistForm(data={'text': 'wrong user'})
        form.instance.user = alice
        form.instance.project = p

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [models.INVALID_USER_ERROR])

    def test_can_save_to_actionlist_when_project_has_duplicate(self):
        p = factories.ProjectFactory(user=alice)
        a = factories.ActionlistItemFactory(user=alice, project=p, text='dupe')

        form = forms.ActionlistForm(data={'text': 'dupe'})
        form.instance.user = alice

        self.assertTrue(form.is_valid())

    def test_shows_only_one_error_when_duplicate_action_on_project(self):
        p = factories.ProjectFactory(user=alice)
        a = factories.ActionlistItemFactory(user=alice, project=p, text='dupe')

        form = forms.ActionlistForm(data={'text': 'dupe'})
        form.instance.user = alice
        form.instance.project = p

        self.assertFalse(form.is_valid())
        self.assertSequenceEqual(form.errors[NON_FIELD_ERRORS],
            [forms.DUPLICATE_ACTION_ERROR])
        self.assertSequenceEqual(list(form.errors.keys()), [NON_FIELD_ERRORS])


class CompleteActionFormTest(TestCase):
    def test_form_save(self):
        item = factories.ActionlistItemFactory(user=alice)
        form = forms.CompleteActionForm()

        form.save(item, alice)

        self.assertTrue(item.complete)

    def test_form_invalid_for_wrong_user(self):
        item = factories.ActionlistItemFactory(user=alice)
        form = forms.CompleteActionForm()

        form.is_valid()
        form.save(item, trudy)

        self.assertFalse(item.complete)
        self.assertEqual(form.errors[NON_FIELD_ERRORS], [forms.ILLEGAL_ACTION_ERROR])

    def test_form_toggles_true_to_false(self):
        item = factories.ActionlistItemFactory(user=alice, complete=True)
        form = forms.CompleteActionForm()

        form.save(item, alice)

        self.assertFalse(item.complete)


class ConvertInlistToActionFormTest(TestCase):
    def test_form_save_creates_action_item(self):
        item = factories.InlistItemFactory(user=alice)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})
        self.assertEqual(models.ActionlistItem.objects.count(), 0)

        form.is_valid()
        form.save(item, alice)

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        self.assertEqual(models.ActionlistItem.objects.first().text,
            item.text)

    def test_form_save_deletes_inlist_item(self):
        item = factories.InlistItemFactory(user=alice)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})
        self.assertEqual(models.InlistItem.objects.count(), 1)

        form.is_valid()
        form.save(item, alice)

        self.assertEqual(models.InlistItem.objects.count(), 0)

    def test_form_invalid_for_wrong_user(self):
        item = factories.InlistItemFactory(user=alice)
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        form.is_valid()
        form.save(item, trudy)

        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [forms.ILLEGAL_ACTION_ERROR])

    def test_form_invalid_for_duplicate_action_text(self):
        factories.ActionlistItemFactory(user=alice, text='duplicate')
        item = factories.InlistItemFactory(user=alice, text='duplicate')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        form.is_valid()
        form.save(item, alice)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.DUPLICATE_ACTION_ERROR])
        self.assertEqual(models.ActionlistItem.objects.count(), 1)

    def test_form_valid_for_duplicate_action_text_for_other_user(self):
        factories.ActionlistItemFactory(user=bob, text='not dupe')
        item = factories.InlistItemFactory(user=alice, text='not dupe')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        self.assertEqual(models.ActionlistItem.objects.count(), 1)
        form.is_valid()
        form.save(item, alice)

        self.assertTrue(form.is_valid())
        self.assertEqual(models.ActionlistItem.objects.count(), 2)

    def test_form_invalid_for_empty_text(self):
        item = factories.InlistItemFactory(user=alice, text='')
        form = forms.ConvertInlistToActionForm(data={'text': item.text})

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['text'], [forms.EMPTY_TEXT_ERROR])


class CreateProjectFormTest(TestCase):
    def test_crispy_helper_is_set(self):
        form = forms.CreateProjectForm()
        self.assertIsInstance(form.helper, FormHelper)

    def test_form_save(self):
        self.assertEqual(models.Project.objects.count(), 3)
        form = forms.CreateProjectForm(data={'name': 'test',
            'description': 'test description'})
        form.instance.user = alice

        form.is_valid()
        project = form.save()

        self.assertEqual(models.Project.objects.count(), 4)

    def test_form_validation_for_empty_name(self):
        form = forms.CreateProjectForm(data={'name': '', 'description': 'test'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], [forms.EMPTY_PROJECT_NAME_ERROR])

    def test_form_validation_for_duplicate_projects(self):
        factories.ProjectFactory(name='dupe', user=alice)
        form = forms.CreateProjectForm(data={'name': 'dupe'})
        form.instance.user = alice

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], [forms.DUPLICATE_PROJECT_ERROR])

    def test_form_validation_for_duplicate_projects_from_different_users(self):
        factories.ProjectFactory(name='dupe', user=bob)
        form = forms.CreateProjectForm(data={'name': 'dupe'})
        form.instance.user = alice

        self.assertTrue(form.is_valid())


class EditProjectFormTest(TestCase):
    def setUp(self):
        self.project = factories.ProjectFactory(user=alice)

    def test_crispy_helper_is_set(self):
        form = forms.EditProjectForm()
        self.assertIsInstance(form.helper, FormHelper)

    def test_form_save(self):
        self.assertEqual(models.Project.objects.count(), 4)
        form = forms.EditProjectForm(data={'name': 'test',
            'description': 'test description'})
        form.instance = self.project

        form.is_valid()
        saved = form.save()

        # No new project got added
        self.assertEqual(models.Project.objects.count(), 4)
        self.assertEqual(saved.pk, self.project.pk)
        self.assertEqual(saved.name, 'test')
        self.assertEqual(saved.description, 'test description')

    def test_form_validation_for_empty_name(self):
        form = forms.EditProjectForm(data={'name': ''})
        form.instance = self.project

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], [forms.EMPTY_PROJECT_NAME_ERROR])

    def test_form_validation_for_duplicate_projects(self):
        dupe = factories.ProjectFactory(name='dupe', user=alice)
        form = forms.EditProjectForm(data={'name': 'dupe'})
        form.instance = self.project

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['name'], [forms.DUPLICATE_PROJECT_ERROR])

    def test_form_validation_for_duplicate_projects_from_different_users(self):
        factories.ProjectFactory(name='dupe', user=bob)
        form = forms.EditProjectForm(data={'name': 'dupe'})
        form.instance = self.project
        self.assertTrue(form.is_valid())


class EditActionFormTest(TestCase):
    def setUp(self):
        self.action = factories.ActionlistItemFactory(user=alice)

    def test_cripsy_helper_is_set(self):
        form = forms.EditActionForm(instance=self.action)
        self.assertIsInstance(form.helper, FormHelper)

    def test_changes_action_to_project(self):
        project = factories.ProjectFactory(user=alice)
        form = forms.EditActionForm(data={'project': project.pk,
            'text': self.action.text}, instance=self.action)

        form.is_valid()
        saved = form.save()

        self.assertEqual(saved.project, project)

    def test_changes_action_to_action_list(self):
        project = factories.ProjectFactory(user=alice)
        form = forms.EditActionForm(data={'project': project.pk,
            'text': self.action.pk}, instance=self.action)

        self.assertTrue(form.is_valid())
        saved = form.save()

        self.assertEqual(saved.project, project)

    def test_cannot_move_to_project_of_different_user(self):
        project = factories.ProjectFactory(user=bob)
        form = forms.EditActionForm(data={'project': project.pk},
            instance=self.action)
        self.assertFalse(form.is_valid())

    def test_only_shows_projects_belonging_to_user(self):
        factories.ProjectFactory.create_batch(2, user=bob)
        projects = factories.ProjectFactory.create_batch(3, user=alice)

        form = forms.EditActionForm(instance=self.action)

        choices = [pk for (pk, text) in form.fields['project'].choices]
        self.assertIn(projects[0].pk, choices)
        self.assertIn(projects[1].pk, choices)
        self.assertIn(projects[2].pk, choices)
        self.assertEqual(len(choices), 4)

    def test_there_is_no_empty_label(self):
        form = forms.EditActionForm(instance=self.action)
        self.assertNotIn('',
            [item[0] for item in form.fields['project'].choices])

    def test_move_causes_duplication_shows_correct_error(self):
        project = factories.ProjectFactory(user=alice)
        action2 = factories.ActionlistItemFactory(user=alice, project=project,
            text=self.action.text)

        form = forms.EditActionForm(data={'project': project.pk},
            instance=self.action)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [forms.DUPLICATE_MOVE_ERROR])

    def test_can_change_deadline_on_action(self):
        self.assertIsNone(self.action.deadline)
        form = forms.EditActionForm(instance=self.action,
            data={'deadline_0': '1970-01-01', 'deadline_1': '00:00:00',
            'project': self.action.project.pk, 'text': self.action.text})

        self.assertTrue(form.is_valid())
        form.save()

        self.assertEquals(str(self.action.deadline),
            '1970-01-01 00:00:00+00:00')

    def test_can_change_text_of_action(self):
        form = forms.EditActionForm(instance=self.action,
            data={'text': 'lvl up', 'project': self.action.project.pk})
        form.save()
        self.assertEqual(self.action.text, 'lvl up')

    def test_changing_text_to_duplicate_shows_correct_error(self):
        action2 = factories.ActionlistItemFactory(user=alice)

        form = forms.EditActionForm(data={'text': self.action.text,
            'project': self.action.project.pk}, instance=action2)

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors[NON_FIELD_ERRORS],
            [forms.DUPLICATE_MOVE_ERROR])
