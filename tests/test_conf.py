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
"""Test configs."""
from __future__ import absolute_import, print_function, unicode_literals

import pytest

import gimme.settings
from gimme.app import create_app


@pytest.mark.parametrize("tinput,texpected", [
    ('derp', False),
    ('', False),
    ('snek', False),
    ('🐍', False),
    ('0', False),
    ('1', True),
    ('t', True),
    ('true', True),
    ('y', True),
    ('yes', True),
])
def test_bool_from_env(tinput, texpected):
    """Test the bool_from_env helper."""
    import os
    os.environ['GIMME_TEST_BOOL'] = tinput.encode('utf-8')
    assert gimme.settings.bool_from_env('GIMME_TEST_BOOL') is texpected
    os.environ.clear()


def test_production_config():
    """Production config."""
    app = create_app(gimme.settings.Production)
    assert app.config['ENV'] == 'production'
    assert app.config['DEBUG'] is False


def test_dev_config():
    """Development config."""
    app = create_app(gimme.settings.Development)
    assert app.config['ENV'] == 'development'
    assert app.config['DEBUG'] is True


def test_test_config():
    """Testing config."""
    app = create_app(gimme.settings.Testing)
    assert app.config['ENV'] == 'development'
    assert app.config['DEBUG'] is False
    assert app.config['TESTING'] is True
