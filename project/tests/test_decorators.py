# -*- coding: utf-8 -*-
import unittest
from unittest import mock

from project import decorators as dec

class AnonymousRequiredDecoratorTests(unittest.TestCase):
    def test_anonymous_user(self):
        func = mock.Mock()
        request = mock.Mock()
        request.user.is_authenticated.return_value = False

        decfunc = dec.anonymous_required(func)
        decfunc(request)

        self.assertTrue(func.called)

    def test_logged_in_user(self):
        func = mock.Mock()
        request = mock.Mock()
        request.user.is_authenticated.return_value = True

        decfunc = dec.anonymous_required(func)
        decfunc(request)

        self.assertFalse(func.called)
        self.assertTrue(request.user.is_authenticated.called)
