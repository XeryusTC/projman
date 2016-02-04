# -*- coding: utf-8 -*-
from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Div, Layout, Submit
from django import forms
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.utils.translation import ugettext_lazy as _

from projects import models
from projects.models import DUPLICATE_ACTION_ERROR

EMPTY_TEXT_ERROR = _('You cannot add empty items')
EMPTY_PROJECT_NAME_ERROR = _('You cannot create a project without a name')
DUPLICATE_ITEM_ERROR = _("You've already got this on your list")
DUPLICATE_PROJECT_ERROR = ('You already have this project')
DUPLICATE_MOVE_ERROR = _("This is already planned for that project")
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
            self._errors[NON_FIELD_ERRORS].clear()
            self.add_error(NON_FIELD_ERRORS, DUPLICATE_ACTION_ERROR)

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
            item.complete = not item.complete
            item.save()
        else:
            self.cleaned_data = []
            self.add_error(None, ILLEGAL_ACTION_ERROR)


class ConvertInlistToActionForm(forms.Form):
    text = forms.CharField(error_messages={'required': EMPTY_TEXT_ERROR})

    def __init__(self, *args, **kwargs):
        super(ConvertInlistToActionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'mui-form'
        self.helper.layout = Layout('text',
            Div(Div(ButtonHolder(Submit('submit', _('Convert'))),
                    css_class="mui-col-xs-12"),
                css_class="mui-row"),
        )

    def save(self, item, user):
        if item.user != user:
            self.cleaned_data = []
            self.add_error(None, ILLEGAL_ACTION_ERROR)
        elif models.ActionlistItem.objects.filter(
                text=self.cleaned_data['text'],
                user=user).count():
            self.add_error('text', DUPLICATE_ACTION_ERROR)
        else:
            item.delete()
            action = models.ActionlistItem(user=user,
                text=self.cleaned_data['text'])
            action.save()


class CreateProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('create', _('Create project')))

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'name': [DUPLICATE_PROJECT_ERROR]}
            self._update_errors(e)

    class Meta:
        model = models.Project
        fields = ('name', 'description')
        error_messages = {
            'name': {'required': EMPTY_PROJECT_NAME_ERROR},
        }


class EditProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProjectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('update', _('Update project')))

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'name': [DUPLICATE_PROJECT_ERROR]}
            self._update_errors(e)

    class Meta:
        model = models.Project
        fields = ('name', 'description')
        error_messages = {
            'name': {'required': EMPTY_PROJECT_NAME_ERROR},
        }


class EditActionForm(forms.ModelForm):
    deadline = forms.SplitDateTimeField(required=False)

    def __init__(self, *args, **kwargs):
        super(EditActionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.add_input(Submit('move', _('Move action')))

        self.fields['project'].queryset = models.Project.objects.filter(
            user=self.instance.user)
        self.fields['project'].empty_label = None
        self.fields['project'].label = False

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            self.errors[NON_FIELD_ERRORS].clear()
            self.add_error(NON_FIELD_ERRORS, DUPLICATE_MOVE_ERROR)

    class Meta:
        model = models.ActionlistItem
        fields = ('text', 'project', 'deadline')
