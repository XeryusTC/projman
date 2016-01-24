# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.views import generic as cbv

class SettingsMainView(LoginRequiredMixin, cbv.TemplateView):
    template_name = 'settings/main.html'
