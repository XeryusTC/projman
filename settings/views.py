# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.utils import translation
from django.views import generic as cbv

from settings import forms
from settings import models

class SettingsMainView(LoginRequiredMixin, cbv.UpdateView):
    template_name = 'settings/main.html'
    form_class = forms.SettingsForm

    def get_object(self, queryset=None):
        return self.request.user.settings

    def get_success_url(self):
        translation.activate(self.request.user.settings.language)
        return reverse('settings:main')
