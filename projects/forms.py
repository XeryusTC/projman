# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from projects.models import InlistItem

EMPTY_TEXT_ERROR = _('You cannot add empty items')

class InlistForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(
        {'placeholder': _('What needs to be done?')}),
        error_messages = {
            'required': EMPTY_TEXT_ERROR})

    def save(self, user):
        item = InlistItem(text=self.cleaned_data['text'],
            user=user)
        item.save()
        return item
