# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, FormView
from django.core.urlresolvers import reverse_lazy

from projects.forms import InlistForm
from projects.models import InlistItem

class MainPageView(TemplateView):
    template_name = 'projects/mainpage.html'


class InlistView(FormView):
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
        form.save(self.request.user)
        return super(InlistView, self).form_valid(form)
