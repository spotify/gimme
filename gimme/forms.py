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
"""Forms."""
from __future__ import absolute_import, print_function, unicode_literals

from flask_wtf import FlaskForm
from wtforms import fields, validators


class RequestForm(FlaskForm):
    """Form used to request access to a resource."""

    access = fields.SelectField(
        label='access',
        description='level of access you require',
        choices=[
            ('roles/storage.admin',
             'Administrative access to Cloud Storage'),
            ('roles/compute.instanceAdmin',
             'Administrative access to Compute Engine'),
            ('roles/bigquery.admin',
             'Administrative access to BigQuery'),
            ('roles/container.admin',
             ('Administrative access to Kubernetes and '
              'the Kubernetes API')),
        ],
        validators=[validators.DataRequired()])

    project = fields.StringField(
        label='project',
        description='the project you want access to',
        validators=[validators.DataRequired()])

    period = fields.SelectField(
        label='period',
        description='amount of time you need access',
        choices=[
            (15, '15 minutes'),
            (30, '30 minutes'),
            (60, '1 hour'),
            (120, '2 hours'),
            (240, '4 hours'),
            (480, '8 hours'),
        ],
        coerce=int,
        validators=[validators.DataRequired()])

    target = fields.StringField(
        label='target',
        description='who will be granted the permissions',
        validators=[validators.DataRequired()])

    domain = fields.SelectField(
        label='domain',
        description='domain of the target',
        validators=[validators.DataRequired()],
    )
