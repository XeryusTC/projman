# -*- coding: utf-8 -*-
from django.conf.urls import url

from settings import views

urlpatterns = [
    url(r'^$', views.SettingsMainView.as_view(), name='main'),
    url(r'set_language/$', views.SetLanguageView.as_view(),
        name='set_language'),
    url(r'account/$', views.AccountSettingsView.as_view(),
        name='account'),
    url(r'account/change_password/$', views.ChangePasswordView.as_view(),
        name='change_password'),
]
