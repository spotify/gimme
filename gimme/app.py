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
"""App.

This module providers helper functions to create an application
instance. It follows the Application Factory pattern.
"""
from __future__ import absolute_import, print_function, unicode_literals

from flask import Flask
from flask_dance.contrib.google import make_google_blueprint

from gimme.settings import Production
from gimme.views import ui


def create_app(config_object=Production):
    """An application factory."""
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    app.config.from_envvar('GIMME_SETTINGS', silent=True)

    register_blueprints(app)
    return app


def register_blueprints(app):
    """Register all the blueprints with the app instance."""
    app.register_blueprint(ui)
    app.register_blueprint(
        make_google_blueprint(
            scope=['profile', 'email',
                   'https://www.googleapis.com/auth/cloud-platform']),
        url_prefix='/login')
    return None
