# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.db.utils import IntegrityError
from django.views.generic import TemplateView, FormView, DeleteView, UpdateView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _

from projects import forms, models

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/mainpage.html'


class InlistView(LoginRequiredMixin, FormView):
    template_name = 'projects/inlist.html'
    form_class = forms.InlistForm

    def get_success_url(self):
        return reverse_lazy('projects:inlist')

    def get_context_data(self, **kwargs):
        context = super(InlistView, self).get_context_data(**kwargs)
        context['inlist_items'] = models.InlistItem.objects.filter(
            user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.validate_unique()
        if form.is_valid():
            form.save(self.request.user)
        else:
            return super(InlistView, self).form_invalid(form)
        return super(InlistView, self).form_valid(form)


class InlistItemDelete(LoginRequiredMixin, DeleteView):
    model = models.InlistItem
    success_url = reverse_lazy('projects:inlist')


class ActionlistView(LoginRequiredMixin, FormView):
    template_name = 'projects/actionlist.html'
    form_class = forms.ActionlistForm
    success_url = reverse_lazy('projects:actionlist')

    def get_context_data(self, **kwargs):
        context = super(ActionlistView, self).get_context_data(**kwargs)
        context['actionlist_items'] = models.ActionlistItem.objects.filter(
            user=self.request.user, complete=False)
        context['actionlist_complete'] = models.ActionlistItem.objects.filter(
            user=self.request.user, complete=True)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.validate_unique()
        if form.is_valid():
            form.save(self.request.user)
        else:
            return super(ActionlistView, self).form_invalid(form)
        return super(ActionlistView, self).form_valid(form)


class ActionlistItemDelete(LoginRequiredMixin, DeleteView):
    model = models.ActionlistItem
    success_url = reverse_lazy('projects:actionlist')


class ActionCompleteView(LoginRequiredMixin, FormView):
    form_class = forms.CompleteActionForm
    success_url = reverse_lazy('projects:actionlist')
    template_name = 'projects/actionlistitem_errorform.html'

    def form_valid(self, form):
        form.save(models.ActionlistItem.objects.get(pk=self.kwargs['pk']),
            self.request.user)
        if form.is_valid():
            return super(ActionCompleteView, self).form_valid(form)
        else:
            return super(ActionCompleteView, self).form_invalid(form)
