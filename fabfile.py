# -*- coding: utf-8 -*-
from __future__ import print_function
from fabric.api import env, run, sudo
from fabric.contrib.console import confirm

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
    deploy.settings._settings_prompt(env)
    env.enable = confirm('Enable site (this activates generated config)?')
    env.setup_ssl = confirm('Enable SSL?', default=False)
    deploy.provision._create_dir_structure(env)
    deploy.provision._setup_database(env)
    deploy.settings._deploy_settings_file(env)

    update()

    deploy.provision._build_system_files(env)
    if env.enable:
        deploy.provision._deploy_system_files(env)

def update():
    """Update the source and and associated files."""
    _setup_dir_variables()
    deploy.deploy._get_latest_source(env, REPO_URL)
    deploy.deploy._update_virtualenv(env)
    deploy.deploy._update_static_files(env)
    deploy.deploy._update_database(env)

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

