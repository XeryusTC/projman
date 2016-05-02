# -*- coding: utf-8 -*-
from fabric.api import get, local, prompt, put, settings, sudo
from fabric.context_managers import hide
from fabric.contrib.console import confirm
from fabric.contrib.files import exists
import random
import re
import string

from .util import _get_enable_var, _password_prompt

settings_map = (('db_name', 'PROJMAN_DB_NAME'),
        ('db_user', 'PROJMAN_DB_USER'),
        ('db_pass', 'PROJMAN_DB_PASSWORD'),
        ('email_host', 'PROJMAN_EMAIL_HOST'),
        ('email_port', 'PROJMAN_EMAIL_PORT'),
        ('email_user', 'PROJMAN_EMAIL_HOST_USER'),
        ('email_pass', 'PROJMAN_EMAIL_HOST_PASSWORD'),
    )

def _settings_prompt(env):
    settings = _get_remote_settings(env)
    if settings:
        show = confirm('Settings file found on remote, show its contents?',
            default=True)
        if show:
            for k, v in settings.items():
                print(str(k) + ' = ' + str(v))
        # The secret key is never changed if it is available, other
        # settings can be overwritten
        env.secret_key = settings['PROJMAN_SECRET_KEY']
        # Ask the user if they want to keep the old settings
        keep = confirm('Keep settings?', default=True)
        if keep:
            for e, s in settings_map:
                if s in settings.keys():
                    env[e] = settings[s]

    # Always make sure that some secret key is set
    env.secret_key = _secret_key(env)

    # Each setting is checked whether it is set, this is done so that the
    # user can keep the settings on the server while also needing to
    # enter new settings whenever those are added. Otherwise the user
    # would have to enter all the settings again
    if 'db_name' not in env.keys():
        env.db_name = prompt('Database name: ', default='projman')
    if 'db_user' not in env.keys():
        env.db_user = prompt('Database user: ', default='projman')
    if 'db_pass' not in env.keys():
        env.db_pass = _password_prompt('Database')
    if 'email_host' not in env.keys():
        env.email_host = prompt('Email host: ', default='localhost')
    if 'email_port' not in env.keys():
        env.email_port = prompt('Email port: ', default='587')
    if 'email_user' not in env.keys():
        env.email_user = prompt('Robot email address: ')
    if 'email_pass' not in env.keys():
        env.email_pass = _password_prompt('Email')

def _get_remote_settings(env):
    """Get the EnvironmentFile from the host and return it as a dict."""
    if not exists('/etc/www/gunicorn-{}'.format(env.host)):
        return None
    get('/etc/www/gunicorn-{}'.format(env.host), '/tmp/%(host)s/envvars')
    setting_re = re.compile(r'([A-Z_]+)="(.*)"')
    settings = {}
    with open('/tmp/{}/envvars'.format(env.host), 'r') as f:
        for line in f.readlines():
            m = re.search(setting_re, line)
            settings[m.group(1)] = m.group(2)
    return settings

def _deploy_settings_file(env):
    """Create the EnvirenmentFile as required by systemd."""
    enable = _get_enable_var(env)
    # Check if settings are set up
    try:
        env.secret_key
    except AttributeError:
        _settings_prompt(env)

    # Create the settings file locally
    sed = "sed -i'' s/{org}/'{new}'/g /tmp/{host}/envvars"
    local('mkdir -p /tmp/{host}/'.format(host=env.host))
    local('cp deploy/envvars /tmp/{host}/envvars'.format(host=env.host))
    local(sed.format(host=env.host, org="SITENAME",   new=env.host))
    local(sed.format(host=env.host, org="db_name",    new=env.db_name))
    local(sed.format(host=env.host, org="db_user",    new=env.db_user))
    local(sed.format(host=env.host, org="secret",     new=env.secret_key))
    local(sed.format(host=env.host, org="email_host", new=env.email_host))
    local(sed.format(host=env.host, org="email_pass", new=env.email_pass))
    local(sed.format(host=env.host, org="email_user", new=env.email_user))
    local(sed.format(host=env.host, org="email_port", new=env.email_port))
    with hide('running', 'stdout'):
        local(sed.format(host=env.host, org="db_password", new=env.db_pass))

    if enable:
        sudo('mkdir -p /etc/www')
        put('/tmp/{host}/envvars'.format(host=env.host),
            '/etc/www/gunicorn-{host}'.format(host=env.host), use_sudo=True,
            mode=0640)
        sudo('chown {user}:www-data /etc/www/gunicorn-{host}'.format(
            host=env.host, user=env.user))
        with settings(warn_only=True):
            sudo('systemctl restart gunicorn-{}.service'.format(env.host))

def _secret_key(env, lenght=50):
    try:
        return env.secret_key
    except AttributeError:
        # Try to receive the settings and return its secret key
        settings = _get_remote_settings(env)
        if settings is not None:
            return settings['PROJMAN_SECRET_KEY']

        # If the settings do not exist we generate a new key
        return ''.join([random.SystemRandom().choice(string.digits +
            string.letters + '()+=_-!@#$%^&*') for i in range(50)])
