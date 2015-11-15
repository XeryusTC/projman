# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _

from project.models import InlistItem

class InlistForm(forms.Form):
    text = forms.CharField(widget=forms.TextInput(
        {'placeholder': _('What needs to be done?')}))

    def save(self, user):
        return InlistItem(text=self.cleaned_data['text'],
            user=user)
