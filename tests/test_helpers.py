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
"""Test helpers."""
from __future__ import absolute_import, print_function, unicode_literals

import datetime

import pytest

from gimme.helpers import UTC, check_valid_domain, project_from_field


@pytest.mark.parametrize('tinput,texpected', [
    (('example.com', []), False),
    (('example.com', ['example.example.com']), False),
    (('example.com', ['example.com']), True),
    (('example.com', ['example.com', 'example.example.com']), True),
])
def test_check_valid_domain(tinput, texpected):
    """Test check_valid_domain."""
    assert check_valid_domain(tinput[0], tinput[1]) is texpected


@pytest.mark.parametrize('tinput,texpected', [
    ('https://console.cloud.google.com/home/dashboard?project=test', 'test'),
    ('https://console.cloud.google.com/apis/dashboard?project=test', 'test'),
    (('https://console.cloud.google.com/apis/dashboard?project=test'
      ':evil#hackers'), 'test%3Aevil'),
    (('https://console.cloud.google.com/apis/dashboard?project=test'
      ';evil#hackers'), 'test'),
    ('https://console.cloud.google.com/home/dashboard?ted=test', ''),
    ('http://test.com', ''),
    ('haha-har', 'haha-har'),
    ('test;evil%har#hackers@', 'test%3Bevil%25har%23hackers%40'),
])
def test_check_project_from_field(tinput, texpected):
    """Test project_from_field."""
    assert project_from_field(tinput) == texpected


def test_utc():
    """Test the UTC object."""
    utc = UTC()
    assert utc.utcoffset(0) == datetime.timedelta(0)
    assert utc.tzname(0) == 'UTC'
    assert utc.dst(0) == datetime.timedelta(0)

    # Ensure the timedelta has no effect
    assert utc.utcoffset(20) == datetime.timedelta(0)
    assert utc.tzname(20) == 'UTC'
    assert utc.dst(20) == datetime.timedelta(0)
