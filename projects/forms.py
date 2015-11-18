# -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext_lazy as _

from projects.models import InlistItem

EMPTY_TEXT_ERROR = _('You cannot add empty items')
DUPLICATE_ITEM_ERROR = _("You've already got this on your list")

class InlistForm(forms.ModelForm):
    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)

    class Meta:
        model = InlistItem
        fields = ('text',)
        widgets = {'text': forms.TextInput(
            {'placeholder': _('What needs to be done?')},
        )}
        error_messages = {
            'text': {'required': EMPTY_TEXT_ERROR},
            NON_FIELD_ERRORS: {'unique_together': DUPLICATE_ITEM_ERROR},
        }
