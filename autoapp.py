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
"""Autoapp, used by flask CLI.

Set the FLASK_APP environment variable to autoapp.py and
run `flask run`.
"""
import gimme.settings
from gimme.app import create_app

CONFIG = gimme.settings.Production


if gimme.settings.bool_from_env('GIMME_DEV'):
    CONFIG = gimme.settings.Development

app = create_app(config_object=CONFIG)
