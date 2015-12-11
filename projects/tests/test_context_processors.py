# -*- coding:utf-8 -*-
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase, RequestFactory

from projects import context_processors as cp
from projects import factories

User = get_user_model()

class ProjectNamesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ProjectNamesTests, cls).setUpClass()
        cls.alice = User.objects.create_user('alice', 'alice@test.org', 'alice')
        cls.bob = User.objects.create_user('bob', 'bob@test.org', 'bob')
        cls.factory = RequestFactory()

    def test_project_list_is_present(self):
        request = self.factory.get('/')
        request.user = self.alice
        self.assertIn('project_list', cp.project_list(request))

    def test_project_list_is_empty_for_anonymous_user(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        self.assertEqual(cp.project_list(request)['project_list'], [])

    def test_project_list_contains_users_projects(self):
        projects = factories.ProjectFactory.create_batch(size=10,
            user=self.alice)
        request = self.factory.get('/')
        request.user = self.alice

        project_list = cp.project_list(request)['project_list']
        for p in projects:
            self.assertIn(p, project_list,
                msg="{} is not found in {}".format(p, project_list))
        self.assertEqual(len(projects), project_list.count())

    def test_project_list_does_not_contain_other_users_projects(self):
        ap = factories.ProjectFactory(user=self.alice)
        bp = factories.ProjectFactory(user=self.bob)
        request = self.factory.get('/')
        request.user = self.alice

        project_list = cp.project_list(request)['project_list']

        self.assertEqual(project_list.count(), 1)
        self.assertIn(ap, project_list)
        self.assertNotIn(bp, project_list)
