# -*- coding: utf-8 -*-
from getpass import getpass

def _enable_env_vars(env):
    return prefix('export $(cat /etc/www/gunicorn-{host}|xargs)'.format(
        host=env.host))

def _password_prompt(name):
    pass1 = 1
    pass2 = 2
    while pass1 != pass2:
        pass1 = getpass('{name} password: '.format(name=name))
        pass2 = getpass('Confirm {name} password: '.format(name=name))
        if pass1 != pass2:
            print('{name} passwords are not the same, try again'.format(
                name=name))
    return pass1

def _get_enable_var(env):
    try:
        return env.enable
    except AttributeError:
        return False
