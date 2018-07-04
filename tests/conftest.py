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
"""Fixtures."""
from __future__ import absolute_import, print_function, unicode_literals

import time

import pytest

from gimme.app import create_app
from gimme.settings import Testing


@pytest.fixture
def app():
    """Creates an app fixture with the testing configuration."""
    app = create_app(config_object=Testing)
    yield app


@pytest.fixture
@pytest.mark.freeze_time('2018-05-04')
def loggedin_app(app):
    """Creates a logged-in test client instance."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['domain'] = 'example.com'
            sess['account'] = 'test@example.com'
            sess['google_oauth_token'] = {
                'access_token': 'tenarsotenarsoetinars',
                'id_token': 'sotieanrsoietnarst',
                'token_type': 'Bearer',
                'expires_in': '3600',
                'expires_at': time.time() + 3600,
            }
        yield client


@pytest.fixture
@pytest.mark.freeze_time('2018-05-04')
def invalid_loggedin_app(app):
    """Creates a logged-in test client instance with an invalid domain."""
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['domain'] = 'example.org'
            sess['account'] = 'test@example.org'
            sess['google_oauth_token'] = {
                'access_token': 'tenarsotenarsoetinars',
                'id_token': 'sotieanrsoietnarst',
                'token_type': 'Bearer',
                'expires_in': '3600',
                'expires_at': time.time() + 3600,
            }
        yield client


@pytest.fixture
@pytest.mark.freeze_time('2018-05-04')
def incomplete_loggedin_app(app):
    """Creates a logged-in test client instance.

    This instances misses the keys in the session we require and will therefore
    trigger a lookup of the profile information
    """
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess['google_oauth_token'] = {
                'access_token': 'tenarsotenarsoetinars',
                'id_token': 'sotieanrsoietnarst',
                'token_type': 'Bearer',
                'expires_in': '3600',
                'expires_at': time.time() + 3600,
            }
        yield client
