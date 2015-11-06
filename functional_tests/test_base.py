# -*- coding: utf-8 -*-

from .base import FunctionalTestCase
import unittest
from unittest import mock

class TestBaseFuctionalTest(unittest.TestCase):
    def test_assertelementpresent_can_find_string(self):
        e = [mock.Mock(text='test')]
        ft = FunctionalTestCase()
        ft.assertElementPresent(e, 'test')

    def test_assertelementpresent_raises_when_string_not_found(self):
        e = [mock.Mock(text='some string')]
        ft = FunctionalTestCase()
        with self.assertRaises(AssertionError):
            ft.assertElementPresent(e, 'test')

    def test_assertelementpresent_returns_element_found(self):
        e = [mock.Mock(text='test'), mock.Mock(text='some string')]
        ft = FunctionalTestCase()
        ret = ft.assertElementPresent(e, 'test')
        self.assertEquals(e[0], ret)
