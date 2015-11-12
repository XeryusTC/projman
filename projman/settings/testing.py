# -*- coding: utf-8 -*-
from .base import *
from .util import get_env_setting

TEST_EMAIL_HOST = get_env_setting('PROJMAN_TEST_EMAIL_HOST')
TEST_EMAIL_ACCOUNT = get_env_setting('PROJMAN_TEST_EMAIL_ACCOUNT')
TEST_EMAIL_PASSWORD = get_env_setting('PROJMAN_TEST_EMAIL_PASSWORD')
