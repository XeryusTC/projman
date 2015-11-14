# -*- coding: utf-8 -*-
import unittest

from project.forms import InlistForm

class InlistFormTest(unittest.TestCase):
    def test_inlist_form_placeholder_set(self):
        form = InlistForm()
        self.assertIn('placeholder="What needs to be done?"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = InlistForm(data={'text': ''})
        self.assertFalse(form.is_valid())
