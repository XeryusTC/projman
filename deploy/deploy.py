# -*- coding: utf-8 -*-

from fabric.api import local, run
from fabric.contrib.files import exists

from .util import _enable_env_vars

def _get_latest_source(env, repo_url):
    if exists('{}/.git'.format(env.source_dir)):
        run('cd {dir} && git fetch'.format(dir=env.source_dir))
    else:
        run('git clone {repo} {dir}'.format(dir=env.source_dir, repo=repo_url))
    current_commit = local('git log -n 1 --format=%H', capture=True)
    run('cd {dir} && git reset --hard {commit}'.format(dir=env.source_dir,
        commit=current_commit))

def _update_virtualenv(env):
    if not exists(env.virtualenv_dir + '/bin/python'):
        run('virtualenv --python=python3 {}'.format(env.virtualenv_dir))
    run('{venv}/bin/pip install -r {source}/requirements/production.txt' \
        .format(venv=env.virtualenv_dir, source=env.source_dir))

def _update_static_files(env):
    with _enable_env_vars(env):
        run('cd {source} && ../virtualenv/bin/python3 manage.py \
                collectstatic --noinput'.format(source=env.source_dir))

def _update_database(env):
    with _enable_env_vars(env):
        run('cd {dir} && ../virtualenv/bin/python3 manage.py migrate \
                --noinput'.format(dir=env.source_dir))
