# -*- coding:utf-8 -*-
from projects import models

def project_list(request):
    if not request.user.is_authenticated():
        return {'project_list': []}
    return {'project_list': models.Project.objects.filter(user=request.user)}
