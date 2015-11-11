# -*- coding: utf-8 -*-

from unipath import Path
import subprocess

THIS_FOLDER = Path(__file__).parent

def reset_database(host):
    subprocess.check_call(['fab', 'reset_database', '--host={}'.format(host)],
        cwd=THIS_FOLDER)

def create_user(host, user, email, password):
    subprocess.check_call(['fab', 'create_user:user={},pass={},email={}' \
        .format(user, password, email), '--host={}'.format(host)],
        cwd=THIS_FOLDER)
