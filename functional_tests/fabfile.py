# -*- coding: utf-8 -*-

from fabric.api import env, run

def _get_base_folder(host):
    return '/var/www/sites/{}'.format(host)

def _get_manage_py(host):
    command = 'export $(cat /etc/www/gunicorn-{host}|xargs) && \
        {path}/virtualenv/bin/python {path}/source/manage.py'.format(
                host=host, path=_get_base_folder(host))
    return command

def reset_database():
    run('{manage} flush --noinput'.format(manage=_get_manage_py(env.host)))

def create_user(user, password, email):
    run('{manage} create_user {username} {password} {email}'.format(
        username=user, password=password, email=email,
        manage=_get_manage_py(env.host)))

def get_sitename():
    name = run('{manage} get_sitename'.format(manage=_get_manage_py(env.host)))
    print name

def create_project(user, name, description=''):
    project = run('{manage} create_project {user} {name} --description {desc}'
        .format(manage=_get_manage_py(env.host), user=user, name=name,
            desc=description))
    print project

def create_action(user, text, project=''):
    if project == '':
        p = run('{manage} create_action {user} \'{text}\''
            .format(manage=_get_manage_py(env.host), user=user, text=text))
    else:
        p = run('{manage} create_action {user} \'{text}\' --project {project}'
            .format(manage=_get_manage_py(env.host), user=user, text=text,
                project=project))
    print p
