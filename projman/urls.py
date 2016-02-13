"""projman URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
import django.views.defaults as default_views

import allauth.urls
import projects.urls
import settings.urls

from landing.views import LandingView

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
]

urlpatterns += i18n_patterns(
    url(r'^accounts/', include(allauth.urls)),
    url(r'^projects/', include(projects.urls, namespace='projects')),
    url(r'^$', LandingView.as_view(), name='landingpage'),
    url(r'^settings/', include(settings.urls, namespace='settings')),

    url('^403/$', default_views.permission_denied, {'exception': None}),
    url('^500/$', default_views.server_error),
)
