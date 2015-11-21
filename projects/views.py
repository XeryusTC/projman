# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.db.utils import IntegrityError
from django.views.generic import TemplateView, FormView, DeleteView
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator

from projects.forms import ActionlistForm, InlistForm, DUPLICATE_ITEM_ERROR
from projects.models import InlistItem, ActionlistItem

class MainPageView(LoginRequiredMixin, TemplateView):
    template_name = 'projects/mainpage.html'


class InlistView(LoginRequiredMixin, FormView):
    template_name = 'projects/inlist.html'
    form_class = InlistForm

    def get_success_url(self):
        return reverse_lazy('projects:inlist')

    def get_context_data(self, **kwargs):
        context = super(InlistView, self).get_context_data(**kwargs)
        context['inlist_items'] = InlistItem.objects.filter(
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
    model = InlistItem
    success_url = reverse_lazy('projects:inlist')


class ActionlistView(LoginRequiredMixin, FormView):
    template_name = 'projects/actionlist.html'
    form_class = ActionlistForm
    success_url = reverse_lazy('projects:actionlist')

    def get_context_data(self, **kwargs):
        context = super(ActionlistView, self).get_context_data(**kwargs)
        context['actionlist_items'] = ActionlistItem.objects.filter(
            user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.validate_unique()
        if form.is_valid():
            form.save(self.request.user)
        else:
            return super(ActionlistView, self).form_invalid(form)
        return super(ActionlistView, self).form_valid(form)
