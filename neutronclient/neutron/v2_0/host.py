# Copyright 2013 OpenStack LLC.
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
# Copyright (c) 2013-2015 Wind River Systems, Inc.
#

# vim: tabstop=4 shiftwidth=4 softtabstop=4

from __future__ import print_function

import logging

from neutronclient._i18n import _
from neutronclient.neutron import v2_0 as neutronV20


def _format_agents_brief(component):
    try:
        return len(component['agents'])
    except Exception:
        return ''


class ListHost(neutronV20.ListCommand):
    """List hosts."""

    resource = 'host'
    log = logging.getLogger(__name__ + '.ListHost')
    list_columns = ['id', 'name', 'availability',
                    'agents', 'subnets', 'routers', 'ports']
    _formatters = {'agents': _format_agents_brief}


class ShowHost(neutronV20.ShowCommand):
    """Show agent information of a given host."""

    resource = 'host'
    log = logging.getLogger(__name__ + '.ShowHost')
    allow_names = True
    json_indent = 5


class CreateHost(neutronV20.CreateCommand):
    """Create a host record."""

    resource = 'host'
    log = logging.getLogger(__name__ + '.CreateHost')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--availability',
            dest='availability', default='down', choices=['up', 'down'],
            help='Set host availability status to up or down')
        parser.add_argument(
            '--id',
            dest='id',
            help='Create a new host record')
        parser.add_argument(
            'name', metavar='NAME',
            help='System hostname of given host')

    def args2body(self, parsed_args):
        body = {'host': {
            'id': parsed_args.id,
            'name': parsed_args.name,
            'availability': parsed_args.availability}, }
        return body


class UpdateHost(neutronV20.UpdateCommand):
    """Update a given host."""

    log = logging.getLogger(__name__ + '.UpdateHost')
    resource = 'host'
    allow_names = True

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--availability',
            dest='availability', default='down', choices=['up', 'down'],
            help='Set host availability status to up or down')

    def args2body(self, parsed_args):
        body = {'host': {
            'availability': parsed_args.availability}}
        return body


class DeleteHost(neutronV20.DeleteCommand):
    """Delete a given host."""

    log = logging.getLogger(__name__ + '.DeleteHost')
    resource = 'host'
    allow_names = True


class BindInterface(neutronV20.UpdateCommand):
    """Bind an interface to a set of provider networks."""

    log = logging.getLogger(__name__ + '.BindInterface')
    resource = 'host'
    allow_names = True

    def call_api(self, neutron_client, host_id, body):
        return neutron_client.host_bind_interface(host_id, body)

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--interface', dest='interface',
            required=True,
            help='Interface UUID value')
        parser.add_argument(
            '--mtu', dest='mtu',
            type=int,
            required=True,
            help='MTU value of the interface')
        parser.add_argument(
            '--providernets', default='', dest='providernets',
            required=True,
            help='Comma separated list of provider network names')
        parser.add_argument(
            '--vlans', metavar='VLANS', default='', dest='vlans',
            help='Comma separated list of vlans reserved for system use')
        parser.add_argument(
            '--test', default=False,
            dest='test', action='store_true',
            help=('Tests whether the bind operation would succeed. '
                  'No action is actually taken'))

    def args2body(self, parsed_args):
        body = {'interface':
                {'uuid': parsed_args.interface,
                 'mtu': parsed_args.mtu,
                 'providernets': parsed_args.providernets,
                 'vlans': parsed_args.vlans}}
        if parsed_args.test:
            body['test'] = True
        return body

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        self.call_api(neutron_client, _id, body)
        print((_('Bound provider networks to interface %(interface)s '
                 'on %(host)s') %
               {'interface': parsed_args.interface, 'host': parsed_args.id}),
              file=self.app.stdout)


class UnbindInterface(neutronV20.UpdateCommand):
    """Unbind an interface from all provider networks."""

    log = logging.getLogger(__name__ + '.UnbindInterface')
    resource = 'host'
    allow_names = True

    def call_api(self, neutron_client, host_id, body):
        return neutron_client.host_unbind_interface(host_id, body)

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--interface', dest='interface',
            required=True,
            help='Interface UUID value')

    def args2body(self, parsed_args):
        body = {'interface':
                {'uuid': parsed_args.interface}}
        return body

    def run(self, parsed_args):
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        body = self.args2body(parsed_args)
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       self.resource,
                                                       parsed_args.id)
        self.call_api(neutron_client, _id, body)
        print((_('Unbound provider networks from interface %(interface)s '
                 'on %(host)s') %
               {'interface': parsed_args.interface, 'host': parsed_args.id}),
              file=self.app.stdout)
