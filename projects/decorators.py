# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import redirect
from functools import wraps

def anonymous_required(func):
    @wraps(func)
    def as_view(request, *args, **kwargs):
        if request.user.is_authenticated():
            dest = kwargs.get('next', settings.LOGIN_REDIRECT_URL)
            return redirect(dest)
        return func(request, *args, **kwargs)
    return as_view

