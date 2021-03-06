# -*- coding: utf-8 -*-
import allauth.account.views
from braces.views import LoginRequiredMixin
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.utils import translation
from django.views import generic as cbv

from settings import forms

class SettingsMainView(LoginRequiredMixin, cbv.UpdateView):
    template_name = 'settings/main.html'
    form_class = forms.SettingsForm

    def get_object(self, queryset=None):
        return self.request.user.settings

    def get_success_url(self):
        translation.activate(self.request.user.settings.language)
        return reverse('settings:main')


class SetLanguageView(cbv.View):
    def get(self, request, *args, **kwargs):
        # This is a somewhat hackish way of getting the most specific
        # available language
        language = translation.get_language_from_path('/{}/'.format(
            request.user.settings.language))

        translation.activate(language)
        if hasattr(request, 'session'):
            request.session[translation.LANGUAGE_SESSION_KEY] = language

        return HttpResponseRedirect(reverse('projects:main'))


class AccountSettingsView(LoginRequiredMixin, cbv.TemplateView):
    template_name = 'settings/account.html'

    def get_context_data(self, **kwargs):
        context = super(AccountSettingsView, self).get_context_data(**kwargs)
        context['password_form'] = forms.ChangePasswordForm()
        return context


class ChangePasswordView(allauth.account.views.PasswordChangeView):
    success_url = reverse_lazy('settings:account')
