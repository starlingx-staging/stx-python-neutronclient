# Copyright 2014 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# Copyright (c) 2015 Wind River Systems, Inc.
#

#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import logging

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronV20


def _add_updatable_args(parser):
    parser.add_argument(
        '--inside-addr',
        help=_('Private IP address.'))
    parser.add_argument(
        '--inside_addr',
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--inside-port',
        help=_('Private layer4 protocol port.'))
    parser.add_argument(
        '--inside_port',
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--outside-port',
        help=_('Public layer4 protocol port.'))
    parser.add_argument(
        '--outside_port',
        help=argparse.SUPPRESS)
    parser.add_argument(
        '--protocol',
        help=_('Layer4 protocol port number.'))
    parser.add_argument(
        '--description',
        help=_('User specified text description'))


def _updatable_args2body(parsed_args, body):
    if parsed_args.inside_addr:
        body['portforwarding'].update({'inside_addr':
                                       parsed_args.inside_addr})
    if parsed_args.inside_port:
        body['portforwarding'].update({'inside_port':
                                       parsed_args.inside_port})
    if parsed_args.outside_port:
        body['portforwarding'].update({'outside_port':
                                       parsed_args.outside_port})
    if parsed_args.protocol:
        body['portforwarding'].update({'protocol': parsed_args.protocol})
    if parsed_args.description:
        body['portforwarding'].update({'description': parsed_args.description})


class ListPortForwarding(neutronV20.ListCommand):
    """List port forwarding mappings."""

    resource = 'portforwarding'
    log = logging.getLogger(__name__ + '.ListPortForwarding')
    list_columns = ['id', 'router_id', 'inside_addr', 'inside_port',
                    'outside_port', 'protocol']


class ShowPortForwarding(neutronV20.ShowCommand):
    """Show information for a given port forwarding mapping."""

    resource = 'portforwarding'
    log = logging.getLogger(__name__ + '.ShowPortForwarding')
    allow_names = True
    json_indent = 5


class CreatePortForwarding(neutronV20.CreateCommand):
    """Create a new port forwarding mapping."""

    resource = 'portforwarding'
    log = logging.getLogger(__name__ + '.CreatePortForwarding')

    def add_known_arguments(self, parser):
        _add_updatable_args(parser)
        parser.add_argument(
            'router_id', metavar='ROUTERID',
            help=_('Router instance identifier.'))

    def _get_router_id(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _router_id = neutronV20.find_resourceid_by_name_or_id(
            neutron_client, 'router', parsed_args.router_id)
        return _router_id

    def args2body(self, parsed_args):
        router_id = self._get_router_id(parsed_args)
        body = {'portforwarding': {
                'router_id': router_id}
                }
        _updatable_args2body(parsed_args, body)
        return body


class UpdatePortForwarding(neutronV20.UpdateCommand):
    """Update a given port forwarding mapping."""

    log = logging.getLogger(__name__ + '.UpdatePortForwarding')
    resource = 'portforwarding'
    allow_names = True

    def add_known_arguments(self, parser):
        _add_updatable_args(parser)

    def args2body(self, parsed_args):
        body = {'portforwarding': {}}
        _updatable_args2body(parsed_args, body)
        return body


class DeletePortForwarding(neutronV20.DeleteCommand):
    """Delete a given port forwarding mapping."""

    log = logging.getLogger(__name__ + '.DeletePortForwarding')
    resource = 'portforwarding'
    allow_names = True
