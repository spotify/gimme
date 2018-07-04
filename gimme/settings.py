# -*- coding: utf-8 -*-
#
# Copyright 2018 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Settings."""
from __future__ import absolute_import, print_function, unicode_literals

import os


def bool_from_env(key):
    """Fetch an environment variable as a boolean.

    This will fetch the specified key and return True if the variable
    was set to a number of string representations of True.

    In all other cases, including when the variable was not found, it
    returns False.
    """
    val = os.getenv(key, default=False)
    if val:
        return val.decode('utf-8').lower() in ('1', 't', 'true', 'y', 'yes')
    return False


class Config(object):
    """Base Configuration object.

    This sets a number of useful defaults which can be overriden in
    anything that subclasses it.
    """

    TESTING = False
    ALLOWED_GSUITE_DOMAINS = []
    SECRET_KEY = bytes(os.environ.get('GIMME_SECRET_KEY',
                                      os.urandom(24)))
    GOOGLE_OAUTH_CLIENT_ID = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    SESSION_COOKIE_HTTPONLY = True


class Production(Config):
    """Production configuration.

    Overrides a few things to reflect that we're running in production.
    """

    PREFERRED_URL_SCHEME = 'https'
    ALLOWED_GSUITE_DOMAINS = ['spotify.com']
    SESSION_COOKIE_SECURE = True


class Development(Config):
    """Development configuration.

    This configuration should be loaded when doing local development.
    """

    ENV = 'development'  # this also enables debug mode
    DEBUG = True
    PREFERRED_URL_SCHEME = 'http'
    ALLOWED_GSUITE_DOMAINS = ['spotify.com']
    OAUTHLIB_RELAX_TOKEN_SCOPE = os.environ.get('OAUTHLIB_RELAX_TOKEN_SCOPE')
    OAUTHLIB_INSECURE_TRANSPORT = os.environ.get('OAUTHLIB_INSECURE_TRANSPORT')
    SESSION_COOKIE_SECURE = False


class Testing(Development):
    """Testing configuration.

    Largely the same as the Development configuration but with some
    tweaks to ensure our test suite runs without issues.
    """

    TESTING = True
    DEBUG = False
    ALLOWED_GSUITE_DOMAINS = ['example.com']
    WTF_CSRF_ENABLED = False
