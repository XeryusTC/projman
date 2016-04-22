# -*- coding: utf-8 -*-
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import resolve
from django.test import TestCase, RequestFactory

class RequestFunctionMixin:
    factory = RequestFactory()

    def get_request(self, user, url=None, session={}, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.get(self.url)
        request.user = user
        request.session = session
        return self.view(request, url, **kwargs)

    def post_request(self, user, data={}, url=None, session={}, **kwargs):
        if url == None:
            url = self.url
        request = self.factory.post(self.url, data)
        request.user = user
        request.session = session
        return self.view(request, url, **kwargs)


class ViewTestMixin(RequestFunctionMixin):
    """
    Bundles most of the common functionality of view tests.

    Uses the Django test client to test for correct template usage,
    assumes that there is a user with the name 'alice' and the password
    'alice'. To change this change the values of self.user and self.password.
    The templates should be stored in the templates attribute
    """
    factory = RequestFactory()
    user = 'alice'
    password = 'alice'

    def test_url_resolves_to_view(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def test_view_uses_correct_templates(self):
        # Check if a non-reversed url has been set
        try:
            url = self.explicit_url
        except AttributeError:
            url = self.url

        self.client.login(username=self.user, password=self.password)
        response = self.client.get(url)

        for t in self.templates:
            with self.subTest(template=t):
                self.assertTemplateUsed(response, t)

    def test_login_required_for_view(self):
        response = self.get_request(AnonymousUser())
        self.assertEqual(response.status_code, 302)
        self.assertRegex(response.url,
            r'/en(-us)?/accounts/login/\?next=' + self.url)
