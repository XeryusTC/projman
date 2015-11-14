# -*- coding: utf-8 -*-
from django.views.generic import TemplateView, FormView

from project.forms import InlistForm

class MainPageView(TemplateView):
    template_name = 'project/mainpage.html'

class InlistView(FormView):
    template_name = 'project/inlist.html'
    form_class = InlistForm
