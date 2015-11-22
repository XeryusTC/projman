# -*- coding: utf-8 -*-
from django.conf.urls import url
from projects import views

urlpatterns = [
    url(r'^$', views.MainPageView.as_view(), name='main'),
    url(r'^inlist/$', views.InlistView.as_view(), name='inlist'),
    url(r'^inlist/(?P<pk>[0-9]+)/delete/$', views.InlistItemDelete.as_view(),
        name='delete_inlist'),
    url(r'^actions/$', views.ActionlistView.as_view(), name='actionlist'),
    url(r'^actions/(?P<pk>[0-9]+)/delete/$',
        views.ActionlistItemDelete.as_view(), name='delete_actionlist'),
    url(r'^actions/(?P<pk>[0-9]+)/complete/$',
        views.ActionCompleteView.as_view(), name='complete_action'),
]
