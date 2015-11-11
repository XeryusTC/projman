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
