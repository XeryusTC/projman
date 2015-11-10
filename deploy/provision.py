# -*- coding: utf-8 -*-
from fabric.api import sudo

from . import settings

def _setup_database(env):
    # Test if database user exists, if not then create it
    query = "SELECT 1 FROM pg_roles WHERE rolname='{}'".format(env.db_user)
    db_setup = sudo("psql -tAc \"{query}\"".format(query=query),
        user='postgres')
    if not db_setup:
        sudo("psql -c \"CREATE USER {user} WITH PASSWORD '{pwd}'\"".format(
            user=env.db_user, pwd=env.db_pass), user='postgres')

    # Test if a database is set up, if not then create it and give user access
    command = 'psql -lqt | cut -d \| -f 1 | grep -w {db} | wc -l'.format(
            db=env.db_name)
    db_exists = sudo(command, user='postgres') == '1'
    if not db_exists:
        sudo('psql -c "CREATE DATABASE {db}"'.format(env.db_name),
            user='postgres')
        sudo('psql -c "GRANT ALL PRIVELEGES ON DATABASE {db} TO {user}"'
            .format(db=env.db_name, user=env.db_user), user='postgres')

def _create_dir_structure(env):
    for subdir in ('static', 'virtualenv', 'source'):
        sudo('mkdir -p {dir}/{sub}'.format(dir=env.dest_dir, sub=subdir))
        sudo('chown -R {user}:www-data {dir}'.format(user=env.user,
            dir=env.dest_dir))

def _build_system_files(env):
    # set up systemd to run gunicorn, build the EnvFile first
    settings._deploy_settings_file(env)
    # set up the systemd service
    local('cp deploy/gunicorn-systemd.service.template /tmp/{host}/gunicorn' \
        .format(host=env.host))
    local("sed -i'' s/SITENAME/'{host}'/g /tmp/{host}/gunicorn".format(
        host=env.host))

    # set up a nginx proxy
    local('cp deploy/nginx{ssl}.conf.template /tmp/{host}/nginx'.format(
        host=env.host, ssl=('-ssl' if env.setup_ssl else '')))
    local("sed -i'' s/SITENAME/'{host}'/g /tmp/{host}/nginx".format(
        host=env.host))

def _deploy_system_files(env):
    if not _get_enable_var(env):
        return

    # Enable the gunicorn service
    put('/tmp/{host}/gunicorn'.format(host=env.host),
        '/etc/systemd/system/gunicorn-{host}.service'.format(host=env.host),
        use_sudo=True)
    sudo('systemctl enable gunicorn-{host}.service'.format(host=env.host))
    sudo('systemctl daemon-reload')
    sudo('systemctl restart gunicorn-{host}.service'.format(host=env.host))

    # Enable the nginx proxy
    put('/tmp/{host}/nginx'.format(host=env.host),
        '/etc/nginx/sites-available/{host}'.format(host=env.host),
        use_sudo=True)
    sudo('ln -fs /etc/nginx/sites-available/{host} \
            /etc/nginx/sites-enabled/{host}'.format(host=env.host))
    sudo('systemctl restart nginx')
