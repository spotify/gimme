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

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   session, url_for)
from flask_dance.contrib.google import google
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError

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
    try:
        google.get(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token':
                    current_app.blueprints['google'].token['access_token']},
        )
    except InvalidClientIdError:
        # Our OAuth session apparently expired. We could renew the token
        # and logout again but that seems a bit silly, so for now fake
        # it.
        pass
    session.clear()
    return redirect(url_for('ui.index'))


@ui.errorhandler(InvalidClientIdError)
def token_expired(_):
    """Retrigger the OAuth flow to get a new token.

    The token we get from Google is an online token, and valid for 3600
    seconds. Once it expires we need to get a new one, but without setting
    the token type to offline and storing the refresh token in some kind of
    database, we can't do that. Aside from that, our app never acts on
    behalf of the user when the user isn't there, so it's not actually
    offline.

    When we try to do an action with an expired token it'll raise an
    InvalidClientIdError with the message 'missing required parameter:
    refresh_token'. Here we catch that one, clear the session and then
    redirect to the home screen, which will trigger the OAuth flow
    again and log the user back in with a new token. Since the user has
    already given consent, they won't actually have to do anything,
    they'll just find themselves back on the home page.
    """
    del current_app.blueprints['google'].token
    flash('Your session had expired. Please submit the request again',
          'error')
    return redirect(url_for('ui.index'))
