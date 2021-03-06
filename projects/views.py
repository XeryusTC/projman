# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse_lazy, reverse
from django.db.models import CharField
from django.db.models.functions import Lower
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (TemplateView, FormView, DeleteView,
    UpdateView, DetailView)
from django.views.generic.edit import FormMixin
from django.views.defaults import permission_denied

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

    def dispatch(self, request, *args, **kwargs):
        item = get_object_or_404(models.InlistItem, pk=self.kwargs['pk'])
        # Need to check against AnonymousUser to not break LoginRequiredMixin
        if request.user != item.user and request.user != AnonymousUser():
            raise Http404()
        return super(InlistItemDelete, self).dispatch(request, *args, **kwargs)


class ActionlistItemDelete(LoginRequiredMixin, DeleteView):
    model = models.ActionlistItem

    def get_success_url(self):
        return reverse('projects:project',
            kwargs={'pk': self.object.project.pk})

    def dispatch(self, request, *args, **kwargs):
        item = get_object_or_404(models.ActionlistItem, pk=self.kwargs['pk'])
        # Need to check against AnonymousUser to not break LoginRequiredMixin
        if request.user != item.user and request.user != AnonymousUser():
            raise Http404()
        return super(ActionlistItemDelete, self).dispatch(request, *args, **kwargs)


class ActionCompleteView(LoginRequiredMixin, FormView):
    form_class = forms.CompleteActionForm
    template_name = 'projects/actionlistitem_errorform.html'

    def get_success_url(self):
        item = get_object_or_404(models.ActionlistItem, pk=self.kwargs['pk'])
        return reverse('projects:project', kwargs={'pk': item.project.pk})

    def form_valid(self, form):
        form.save(models.ActionlistItem.objects.get(pk=self.kwargs['pk']),
            self.request.user)
        if form.is_valid():
            return super(ActionCompleteView, self).form_valid(form)
        else:
            return super(ActionCompleteView, self).form_invalid(form)


class InlistItemToActionView(LoginRequiredMixin, FormView):
    template_name = 'projects/convert_inlist_to_action.html'
    form_class = forms.ConvertInlistToActionForm
    success_url = reverse_lazy('projects:inlist')

    def dispatch(self, request, *args, **kwargs):
        self.inlist_item = get_object_or_404(models.InlistItem,
            pk=self.kwargs['pk'])
        # Test if the request came from the right user
        if request.user != self.inlist_item.user \
            and request.user != AnonymousUser():
            raise Http404()

        return super(InlistItemToActionView, self).dispatch(request, *args,
            **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        kwargs = self.get_form_kwargs()
        kwargs['initial'].update({'text': self.inlist_item.text})
        return form_class(**kwargs)

    def form_valid(self, form):
        form.save(self.inlist_item, self.request.user)
        if form.is_valid():
            return super(InlistItemToActionView, self).form_valid(form)
        else:
            return super(InlistItemToActionView, self).form_invalid(form)


class CreateProjectView(LoginRequiredMixin, FormView):
    template_name = 'projects/create_project.html'
    form_class = forms.CreateProjectForm

    def get_initial(self, *args, **kwargs):
        initial = super(CreateProjectView, self).get_initial(*args, **kwargs)
        if 'inlistitem' in self.kwargs.keys():
            initial['name'] = models.InlistItem.objects.get(
                pk=self.kwargs['inlistitem'])
        return initial

    def get_success_url(self):
        return reverse_lazy('projects:project', kwargs={'pk': self.project.pk})

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.validate_unique()
        if form.is_valid():
            self.project = form.save()
            if 'inlistitem' in self.kwargs.keys():
                models.InlistItem.objects.get(pk=self.kwargs['inlistitem']). \
                    delete()
            return super(CreateProjectView, self).form_valid(form)
        else:
            return super(CreateProjectView, self).form_invalid(form)


class ProjectView(LoginRequiredMixin, FormMixin, DetailView):
    template_name = 'projects/project.html'
    model = models.Project
    form_class = forms.ActionlistForm

    def get_success_url(self):
        return reverse_lazy('projects:project', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super(ProjectView, self).get_context_data(**kwargs)
        context['protected'] = (self.object.name == models.ACTION_PROJECT_NAME)
        context['sort_form'] = forms.ActionlistSortForm(
            initial={'return_model': self.object.pk,
            'sort_method': self.request.session['sort_method'],
            'sort_order': self.request.session['sort_order']})

        # Sort the action list
        # Case sensitive fields need to be converted to insensitive
        if self.request.session['sort_method'] == 'text':
            sort = Lower(self.request.session['sort_method'])
            if self.request.session['sort_order'] == '-':
                sort = sort.desc()
            context['actions'] = self.object.action_list.order_by(sort)
        # Other fields can just be sorted regularly
        elif self.request.session['sort_method'] != '':
            context['actions'] = self.object.action_list.order_by(
                self.request.session['sort_order'] + \
                self.request.session['sort_method'])
        # When no ordering is applied just get all actions
        else:
            context['actions'] = self.object.action_list.all()

        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        form.instance.user = self.request.user
        form.instance.project = self.object

        form.validate_unique()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(models.Project, pk=self.kwargs['pk'])

        # Need to check against AnonymousUser to not break LoginRequiredMixin
        if project.user != request.user and request.user != AnonymousUser():
            raise Http404()

        # Set default action sort session data
        if 'sort_method' not in self.request.session:
            self.request.session['sort_method'] = ''
            self.request.session['sort_order'] = ''
        return super(ProjectView, self).dispatch(request, *args, **kwargs)


class EditProjectView(LoginRequiredMixin, UpdateView):
    form_class = forms.EditProjectForm
    model = models.Project
    template_name_suffix = '_edit'

    def get_success_url(self):
        return reverse('projects:project', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(models.Project, pk=self.kwargs['pk'])
        # Need to check against AnonymousUser to not break LoginRequiredMixin
        if request.user != project.user and request.user != AnonymousUser():
            raise Http404()

        # Check whether the project is an action project
        if project.name == models.ACTION_PROJECT_NAME:
            return permission_denied(request, None)

        return super(EditProjectView, self).dispatch(request, *args, **kwargs)


class DeleteProjectView(LoginRequiredMixin, DeleteView):
    model = models.Project
    success_url = reverse_lazy('projects:main')

    def dispatch(self, request, *args, **kwargs):
        project = get_object_or_404(models.Project, pk=self.kwargs['pk'])
        # Need to check against AnonymousUser to not break LoginRequiredMixin
        if request.user != project.user and request.user != AnonymousUser():
            raise Http404()

        # Check whether the project is an action project
        if project.name == models.ACTION_PROJECT_NAME:
            return permission_denied(request, None)

        return super(DeleteProjectView, self).dispatch(request, *args, **kwargs)


class EditActionView(LoginRequiredMixin, UpdateView):
    template_name = 'projects/edit_action.html'
    model = models.ActionlistItem
    form_class = forms.EditActionForm
    context_object_name = 'action'

    def get_success_url(self):
        return reverse('projects:project', kwargs={'pk': self.old_project.pk})

    def post(self, *args, **kwargs):
        self.object = self.get_object()
        self.old_project = self.object.project

        return super(EditActionView, self).post(*args, **kwargs)


class ActionlistSortView(LoginRequiredMixin, FormView):
    form_class = forms.ActionlistSortForm
    template_name = 'generic_form.html'
    http_method_names = ['post']

    def get_success_url(self):
        if self.return_model.user != self.request.user:
            return permission_denied(self.request, None)
        return reverse('projects:project', kwargs={'pk': self.return_model.pk})

    def form_valid(self, form):
        self.request.session['sort_method'] = form.cleaned_data['sort_method']
        self.request.session['sort_order'] = form.cleaned_data['sort_order']
        self.return_model = form.cleaned_data['return_model']
        return super(ActionlistSortView, self).form_valid(form)
