# -*- coding: utf-8 -*-
from django.views.generic import TemplateView

class MainPageView(TemplateView):
    template_name = 'project/mainpage.html'
