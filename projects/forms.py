# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Field, Layout, Submit
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext_lazy as _

from projects import models

EMPTY_TEXT_ERROR = _('You cannot add empty items')
DUPLICATE_ITEM_ERROR = _("You've already got this on your list")
DUPLICATE_ACTION_ERROR = _("You already planned to do this")
ILLEGAL_ACTION_ERROR = _("You are not allowed to do this")

class InlistForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(InlistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'mui-form--inline'
        self.helper.layout = Layout(
            Div(Div('text', css_class="mui-col-xs-8 mui-col-md-6 hide-label"),
                Div(ButtonHolder(Submit('submit', _('Add'))),
                    css_class="mui-col-xs-4 mui-col-md-2"),
                css_class="mui-row"),
        )

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)

    class Meta:
        model = models.InlistItem
        fields = ('text',)
        widgets = {'text': forms.TextInput(
            {'placeholder': _('What needs to be done?')},
        )}
        error_messages = {
            'text': {'required': EMPTY_TEXT_ERROR},
            NON_FIELD_ERRORS: {'unique_together': DUPLICATE_ITEM_ERROR},
        }


class ActionlistForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ActionlistForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'mui-form--inline'
        self.helper.layout = Layout(
            Div(Div('text', css_class="mui-col-xs-8 mui-col-md-6 hide-label"),
                Div(ButtonHolder(Submit('submit', _('Add'))),
                    css_class="mui-col-xs-4 mui-col-md-2"),
            css_class="mui-row")
        )

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ACTION_ERROR]}
            self._update_errors(e)

    class Meta:
        model = models.ActionlistItem
        fields = ('text',)
        widgets = {'text': forms.TextInput(
            {'placeholder': _('What do you need to do?')},
        )}
        error_messages = {
            'text': {'required': EMPTY_TEXT_ERROR},
        }


class CompleteActionForm(forms.Form):
    def save(self, item, user):
        if item.user == user:
            item.complete = True
            item.save()
        else:
            self.cleaned_data = []
            self.add_error(None, ILLEGAL_ACTION_ERROR)
