# -*- coding: utf-8 -*-
from __future__ import print_function
from fabric.api import env, local, prompt, sudo
from fabric.context_managers import prefix
from fabric.contrib.files import exists

import deploy

REPO_URL = 'https://github.com/XeryusTC/projman.git'

def requirements():
    """Install all the software requirements that pip can't manage or
    that don't live in our virtualenv."""
    sudo('apt-get install nginx git python3 python3-pip \
        postgresql-server-dev-9.4')
    sudo('pip3 install virtualenv')

def provision():
    """Create the config files to run the site on the server."""
    _setup_dir_variables()
    _settings_prompt()
    env.enable = confirm('Enable site (this activates genrated config)?')
    env.setup_ssl = confirm('Enable SSL?', default=False)
    _create_folder_structure(env)
    _setup_database(env)
    _deploy_settings_file()

    deploy()

    _build_system_files()
    if env.enable:
        _deploy_system_files()

def deploy():
    """Update the source and and associated files."""
    _setup_dir_variables()
    _get_latest_source(env)
    _update_virtualenv(env)
    _update_static_files(env)
    _update_database(env)

def restart():
    """Restart the gunicorn service."""
    sudo('service gunicorn-{host} restart'.format(host=env.host))

def _setup_dir_variables():
    # Skip if we already done this
    try:
        env.dest_dir
        return
    except AttributeError:
        pass

    run('uptime') # make sure we have a host set
    env.dest_dir = '/var/www/sites/{}'.format(env.host)
    env.source_dir = '{}/source'.format(env.dest_dir)
    env.virtualenv_dir = '{}/virtualenv'.format(env.dest_dir)

