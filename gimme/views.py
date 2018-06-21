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
"""This module contains all the views.

The views are what gets rendered in the browser when people browse to the
different routes.
"""
from __future__ import absolute_import, print_function, unicode_literals

from flask import (Blueprint, current_app, redirect, render_template, session,
                   url_for)
from flask_dance.contrib.google import google

from gimme.forms import RequestForm
from gimme.helpers import add_conditional_binding, login_required

ui = Blueprint('ui', __name__, url_prefix='/')


@ui.route('/', methods=['GET', 'POST'])
@login_required(google)
def index():
    """Renders the home page."""
    form = RequestForm()
    form.domain.choices = [(domain, '@{0}'.format(domain)) for domain in
                           current_app.config['ALLOWED_GSUITE_DOMAINS']]
    if form.validate_on_submit():
        add_conditional_binding(google, form)
        return redirect(url_for('ui.index'))

    return render_template(
        'index.html.j2',
        form=form,
    )


@ui.route('/logout', methods=['GET'])
@login_required(google)
def logout():
    """Revokes token and empties session."""
    google.get(
        'https://accounts.google.com/o/oauth2/revoke',
        params={'token': session['google_oauth_token']['access_token']},
    )
    session.clear()
    return redirect(url_for('ui.index'))
