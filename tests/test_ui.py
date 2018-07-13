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
"""Test the UI."""
from __future__ import absolute_import, print_function, unicode_literals

import responses

from gimme.helpers import CLOUD_RM


def test_not_logged_in(app):
    """Test what happens when we're not logged in.

    Ensure we trigger the OAuth flow if we don't have a valid
    session.
    """
    res = app.test_client().get('/')
    assert ('You should be redirected automatically to target URL: <a href'
            '="/login/google">/login/google</a>').lower() in \
        res.get_data(as_text=True).lower()
    assert res.status_code == 302


def test_invalid_logged_in(invalid_loggedin_app):
    """Test what happens when someone comes from a non-whitelisted domain.

    Ensure that we deny them access.
    """
    res = invalid_loggedin_app.get('/')
    assert res.status_code == 403
    assert 'does not match the configured whitelist' in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_incomplete_loggedin(incomplete_loggedin_app):
    """Test what happens when there's a valid session but no profile info.

    Ensure that we call out to the userinfo OAuth endpoint, fetch and
    store the domain and then grant access.
    """
    responses.add(responses.GET,
                  'https://www.googleapis.com/userinfo/v2/me',
                  status=200, json={
                      'hd': 'example.com',
                      'email': 'test@example.com',
                  })
    res = incomplete_loggedin_app.get('/')
    assert len(responses.calls) == 1
    assert res.content_type == 'text/html; charset=utf-8'
    assert res.status_code == 200


@responses.activate
def test_incomplete_loggedin_profile_failed(incomplete_loggedin_app):
    """Test what happens when we have a valid session but can't get profile info.

    Ensures we deny access if the profile endpoint returns anything
    other than a 200 OK.
    """
    responses.add(responses.GET,
                  'https://www.googleapis.com/userinfo/v2/me',
                  status=404)
    res = incomplete_loggedin_app.get('/')
    assert len(responses.calls) == 1
    assert res.content_type == 'text/html; charset=utf-8'
    assert res.status_code == 403
    assert 'could not get your profile information' in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_incomplete_loggedin_domain_missing(incomplete_loggedin_app):
    """Test what happens when the profile response is incomplete.

    Ensure we deny access if the profile endpoint doesn't return all the
    information we need in order to decide if we should let someone in or
    not.
    """
    responses.add(responses.GET,
                  'https://www.googleapis.com/userinfo/v2/me',
                  status=200, json={})
    res = incomplete_loggedin_app.get('/')
    assert len(responses.calls) == 1
    assert res.content_type == 'text/html; charset=utf-8'
    assert res.status_code == 403
    assert 'incomplete profile information' in \
        res.get_data(as_text=True).lower()


def test_simple_get(loggedin_app):
    """Test what happens when we satisfy all the prerequisites.

    Ensures we render the index page.
    """
    res = loggedin_app.get('/')
    assert res.content_type == 'text/html; charset=utf-8'
    assert res.status_code == 200
    assert '<div class="mui-row messages">' not in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_valid_post(loggedin_app):
    """Test what happens when a form is submitted with correct data.

    Ensures we set the new IAM policy on the target project.
    """
    form = {
        'project': 'test',
        'access': 'roles/compute.instanceAdmin',
        'period': '15',
        'target': 'test4',
        'domain': 'example.com',
        'csrf_token': 'not validated in tests',
    }

    url = '{}/{}:getIamPolicy'.format(CLOUD_RM, 'test')

    responses.add(
        responses.POST, url, status=200,
        json={
            'bindings': [
                {
                    'role': 'roles/owner',
                    'members': [
                        'user:test@exmaple.com',
                        'user:test2@example.com',
                    ],
                },
                {
                    'role': 'roles/storage.admin',
                    'condition': {
                        'expression': 'request.time < timestamp(\'2018-05-04T00:00:00.00+00:00\')',  # noqa: E501
                        'title': 'testing',
                    },
                    'members': [
                        'user:test3@example.com',
                    ],
                },
            ],
            'version': 1,
            'etag': 'test',
        })

    url = '{}/{}:setIamPolicy'.format(CLOUD_RM, 'test')
    responses.add(responses.POST, url, status=200)

    res = loggedin_app.post('/', data=form, follow_redirects=True)
    assert res.status_code == 200
    assert res.content_type == 'text/html; charset=utf-8'
    assert len(responses.calls) == 2
    assert responses.calls[0].request.method == 'POST'
    assert responses.calls[0].request.url == '{}/{}:getIamPolicy'.format(
        CLOUD_RM, 'test')
    assert responses.calls[1].request.method == 'POST'
    assert responses.calls[1].request.url == '{}/{}:setIamPolicy'.format(
        CLOUD_RM, 'test')
    assert 'policy' in responses.calls[1].request.body.decode('utf-8').lower()
    assert 'granted by test@example.com' in \
        responses.calls[1].request.body.decode('utf-8').lower()
    assert 'this is a temporary grant' in \
        responses.calls[1].request.body.decode('utf-8').lower()
    assert 'great success' in res.get_data(as_text=True).lower()


@responses.activate
def test_valid_post_token_expired(loggedin_app, freezer):
    """Test what happens when we try to set a policy but our token has expiredy.

    Ensures the error handler catches the token expiry and retriggers the OAuth
    flow to get a new token.
    """
    freezer.move_to('2018-05-05')
    form = {
        'project': 'test',
        'access': 'roles/compute.instanceAdmin',
        'period': '15',
        'target': 'test4',
        'domain': 'example.com',
        'csrf_token': 'not validated in tests',
    }
    responses.add(
        responses.POST, 'https://accounts.google.com/o/oauth2/token',
        status=400,
        json={
            'error_description': 'Missing required parameter: refresh_token',
            'error': 'invalid_request'})
    res = loggedin_app.post('/', data=form)
    assert res.status_code == 302
    assert ('you should be redirected automatically to target url: '
            '<a href="/">/</a>.') in res.get_data(as_text=True).lower()


@responses.activate
def test_post_invalid_project_url(loggedin_app):
    """Test what happens when we submit an invalid project URL.

    Ensures that we inform the user the information they provided is
    incorrect. This should never call the Cloud Resource Manager.
    """
    form = {
        'project': 'https://console.cloud.google.com/?test=test',
        'access': 'roles/compute.instanceAdmin',
        'period': '15',
        'target': 'test4',
        'domain': 'example.com',
        'csrf_token': 'not validated in tests',
    }
    res = loggedin_app.post('/', data=form, follow_redirects=True)
    assert res.status_code == 200
    assert res.content_type == 'text/html; charset=utf-8'
    assert len(responses.calls) == 0
    assert 'could not find project ID in'.lower() in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_valid_post_failed_get_policy(loggedin_app):
    """Test what happens when we can't fetch the IAM Policy.

    Ensures we inform the user when the policy could not be fetched.
    This usually means the poject name was incorrect or that they
    don't have access to said project.

    This must never trigger a call to setIamPolicy.
    """
    form = {
        'project': 'test',
        'access': 'roles/compute.instanceAdmin',
        'period': '15',
        'target': 'test4',
        'domain': 'example.com',
        'csrf_token': 'not validated in tests',
    }
    url = '{}/{}:getIamPolicy'.format(CLOUD_RM, 'test')
    responses.add(
        responses.POST, url, status=404,
        json={'error': {'message': 'resource not found'}})
    res = loggedin_app.post('/', data=form, follow_redirects=True)
    assert res.status_code == 200
    assert res.content_type == 'text/html; charset=utf-8'
    assert len(responses.calls) == 1
    assert responses.calls[0].request.method == 'POST'
    assert responses.calls[0].request.url == '{}/{}:getIamPolicy'.format(
        CLOUD_RM, 'test')
    assert 'could not fetch IAM policy'.lower() in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_valid_post_failed_set_policy(loggedin_app):
    """Test what happens when we fail to set the policy.

    Ensures that we inform the user when we fail to set the new IAM policy,
    i.e the permissions aren't granted. This can happen if the user has
    viewer rights for example, and therefore can view the IAM policy, but
    lacks the permissions to update it.
    """
    form = {
        'project': 'test',
        'access': 'roles/compute.instanceAdmin',
        'period': '15',
        'target': 'test4',
        'domain': 'example.com',
        'csrf_token': 'not validated in tests',
    }

    url = '{}/{}:getIamPolicy'.format(CLOUD_RM, 'test')
    responses.add(
        responses.POST, url, status=200,
        json={
            'bindings': [
                {
                    'role': 'roles/owner',
                    'members': [
                        'user:test@exmaple.com',
                        'user:test2@example.com',
                    ],
                },
                {
                    'role': 'roles/storage.admin',
                    'condition': {
                        'expression': 'request.time < timestamp(\'2018-05-04T00:00:00.00+00:00\')',  # noqa: E501
                        'title': 'testing',
                    },
                    'members': [
                        'user:test3@example.com',
                    ],
                },
            ],
            'version': 1,
            'etag': 'test',
        })

    url = '{}/{}:setIamPolicy'.format(CLOUD_RM, 'test')
    responses.add(
        responses.POST, url, status=400,
        json={
            'error': {
                'code': 400,
                'detail': [{
                    '@type': 'type.googleapis.com/google.rpc.BadRequest',
                    'fieldViolations': [
                        {'description': 'Invalid JSON payload'}],
                }],
                'status': 'INVALID_ARGUMENT',
                'message': 'Invalid JSON payload received.',
            }})

    res = loggedin_app.post('/', data=form, follow_redirects=True)
    assert res.status_code == 200
    assert res.content_type == 'text/html; charset=utf-8'
    assert len(responses.calls) == 2
    assert 'could not apply new policy'.lower() in \
        res.get_data(as_text=True).lower()


@responses.activate
def test_logout(loggedin_app):
    """Test what happens when we logout the user.

    Ensures we revoke the token and clear the session, which will trigger the
    OAuth flow again.
    """
    responses.add(responses.GET, 'https://accounts.google.com/o/oauth2/revoke',
                  status=200)

    res = loggedin_app.get('/logout')
    assert len(responses.calls) == 1
    assert ('You should be redirected automatically to target URL: <a href'
            '="/">/</a>').lower() in res.get_data(as_text=True).lower()
    assert res.status_code == 302


@responses.activate
def test_logout_expired_token(loggedin_app, freezer):
    """Test what happens when we logout the user but token has expired.

    Ensures we clear the session as we're no longer able to revoke the
    token.
    """
    freezer.move_to('2018-05-05')
    responses.add(
        responses.POST, 'https://accounts.google.com/o/oauth2/token',
        status=400,
        json={
            'error_description': 'Missing required parameter: refresh_token',
            'error': 'invalid_request'})

    res = loggedin_app.get('/logout')
    assert len(responses.calls) == 1
    assert ('You should be redirected automatically to target URL: <a href'
            '="/">/</a>').lower() in res.get_data(as_text=True).lower()
    assert res.status_code == 302


@responses.activate
def test_logout_invalid_login(invalid_loggedin_app):
    """Test what happens when an invalid user tries to log out.

    Ensures we revoke the token and clear the session.
    """
    responses.add(responses.GET, 'https://accounts.google.com/o/oauth2/revoke',
                  status=200)

    res = invalid_loggedin_app.get('/logout')
    assert len(responses.calls) == 1
    assert ('You should be redirected automatically to target URL: <a href'
            '="/">/</a>').lower() in res.get_data(as_text=True).lower()
    assert res.status_code == 302


@responses.activate
def test_logout_not_logged_in(app):
    """Test what happens when we try to logout if we're not logged in.

    Ensures that we clear the session and redirect.
    """
    res = app.test_client().get('/logout')
    assert ('You should be redirected automatically to target URL: <a href'
            '="/">/</a>').lower() in res.get_data(as_text=True).lower()
    assert res.status_code == 302
