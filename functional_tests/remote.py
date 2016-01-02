# -*- coding: utf-8 -*-

from unipath import Path
import subprocess

THIS_FOLDER = Path(__file__).parent

def reset_database(host):
    subprocess.check_call(['fab', 'reset_database', '--host={}'.format(host)],
        cwd=THIS_FOLDER)

def create_user(host, user, email, password):
    subprocess.check_call(['fab', 'create_user:user={},password={},email={}' \
        .format(user, password, email), '--host={}'.format(host)],
        cwd=THIS_FOLDER)

def get_sitename(host):
    return subprocess.check_output(['fab', 'get_sitename',
        '--host={}'.format(host), '--hide=everything,status'],
        cwd=THIS_FOLDER).decode().strip()

def create_project(host, user, name, description=''):
    return subprocess.check_output(['fab',
        'create_project:user={},name={},description={}'.format(user, name,
            description), '--host={}'.format(host)], cwd=THIS_FOLDER)

def create_action(host, user, text, project=''):
    return subprocess.check_output(['fab',
        'create_action:user={},text={},project={}'.format(user, text, project),
        '--host={}'.format(host)], cwd=THIS_FOLDER)
