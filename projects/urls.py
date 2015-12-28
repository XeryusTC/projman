# -*- coding: utf-8 -*-
from django.conf.urls import url
from projects import views

urlpatterns = [
    url(r'^$', views.MainPageView.as_view(), name='main'),
    # Inlist
    url(r'^inlist/$', views.InlistView.as_view(), name='inlist'),
    url(r'^inlist/(?P<pk>[0-9]+)/delete/$', views.InlistItemDelete.as_view(),
        name='delete_inlist'),
    url(r'^inlist/(?P<pk>[0-9]+)/convert/action/$',
        views.InlistItemToActionView.as_view(), name='convert_inlist_action'),
    url(r'^inlist/(?P<inlistitem>[0-9]+)/convert/project/$',
        views.CreateProjectView.as_view(), name='convert_inlist_project'),

    # Actions
    url(r'^actions/$', views.ActionlistView.as_view(), name='actionlist'),
    url(r'^actions/(?P<pk>[0-9]+)/delete/$',
        views.ActionlistItemDelete.as_view(), name='delete_actionlist'),
    url(r'^actions/(?P<pk>[0-9]+)/complete/$',
        views.ActionCompleteView.as_view(), name='complete_action'),
    url(r'^actions/(?P<pk>[0-9]+)/move/$', views.MoveActionView.as_view(),
        name='move_action'),

    # Projects
    url(r'^project/(?P<pk>[0-9]+)/$', views.ProjectView.as_view(),
        name='project'),
    url(r'^project/create/$', views.CreateProjectView.as_view(),
        name='create_project'),
    url(r'project/(?P<pk>[0-9]+)/edit/$', views.EditProjectView.as_view(),
        name='edit_project'),
    url(r'project/(?P<pk>[0-9]+)/delete/$', views.DeleteProjectView.as_view(),
        name='delete'),
]
