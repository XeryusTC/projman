# -*- coding: utf-8 -*-
import allauth.account.forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from settings import models

INLIST_DELETE_CONFIRM_LABEL = _('Ask for confirmation when deleting ' + \
        'inlist item')
ACTION_DELETE_CONFIRM_LABEL = _('Ask for confirmation when deleting actions')

class SettingsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('confirm', _('Save')))

    class Meta:
        model = models.Settings
        exclude = ('user',)
        labels = {
            'language': _('Language'),
            'inlist_delete_confirm': INLIST_DELETE_CONFIRM_LABEL,
            'action_delete_confirm': ACTION_DELETE_CONFIRM_LABEL,
        }


class ChangePasswordForm(allauth.account.forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('settings:change_password')
        self.helper.add_input(Submit('change_password', _('Change password')))
