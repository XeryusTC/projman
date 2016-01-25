# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views import generic as cbv

from settings import forms
from settings import models

class SettingsMainView(LoginRequiredMixin, cbv.UpdateView):
    template_name = 'settings/main.html'
    form_class = forms.SettingsForm
    success_url = reverse_lazy('settings:main')

    def get_object(self, queryset=None):
        return self.request.user.settings
