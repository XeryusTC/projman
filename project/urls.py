# -*- coding: utf-8 -*-
from django.conf.urls import url
from project import views

urlpatterns = [
    url(r'^$', views.MainPageView.as_view(), name='main'),
]