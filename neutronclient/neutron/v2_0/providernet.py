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
# Copyright (c) 2013-2014 Wind River Systems, Inc.
#

#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import itertools
import logging

from oslo_serialization import jsonutils

from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20


def _format_vxlan_attributes(vxlan):
    attributes = dict((k, vxlan[k]) for k in vxlan.keys())
    return '{}'.format(jsonutils.dumps(attributes))


class ListProviderNetType(neutronV20.ListCommand):
    """List provider network types."""

    resource = 'providernet_type'
    log = logging.getLogger(__name__ + '.ListProviderNetType')
    list_columns = ['type', 'description']


def _format_ranges(providernet):
    try:
        ranges = []
        for r in providernet['ranges']:
            ranges.append(dict((k, r[k]) for k in r.keys() if k in
                               ['name', 'minimum', 'maximum']))
    except Exception as e:
        return 'error={}'.format(e)

    return '\n'.join(["{}".format(jsonutils.dumps(r)) for r in ranges])


class ListProviderNet(neutronV20.ListCommand):
    """List provider networks."""

    resource = 'providernet'
    log = logging.getLogger(__name__ + '.ListProviderNet')
    _formatters = {'ranges': _format_ranges, }
    list_columns = ['id', 'name', 'type', 'mtu', 'ranges']


class ShowProviderNet(neutronV20.ShowCommand):
    """Show information for a given provider network."""

    resource = 'providernet'
    log = logging.getLogger(__name__ + '.ShowProviderNet')
    allow_names = True
    json_indent = 5


class CreateProviderNet(neutronV20.CreateCommand):
    """Create a provider network."""

    resource = 'providernet'
    log = logging.getLogger(__name__ + '.CreateProviderNet')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            dest='description',
            help='Set user-defined description field for a provider network')
        parser.add_argument(
            '--type', required=True,
            dest='type', default='flat',
            choices=['flat', 'vlan', 'vxlan'],
            help='Set network type for a provider network')
        parser.add_argument(
            '--mtu', dest='mtu', type=int,
            help='Maximum transmit unit on provider network')
        utils.add_boolean_argument(
            parser,
            '--vlan-transparent',
            default='False',
            help='Allow VLAN tagged packets on tenant networks')
        parser.add_argument(
            'name', metavar='NAME',
            help='Set user-defined name for a provider network')

    def args2body(self, parsed_args):
        body = {'providernet': {
                'name': parsed_args.name,
                'type': parsed_args.type,
                'vlan_transparent': parsed_args.vlan_transparent}
                }

        if parsed_args.mtu:
            body['providernet'].update({'mtu': parsed_args.mtu})

        if parsed_args.description:
            body['providernet'].update({'description':
                                        parsed_args.description})
        return body


class UpdateProviderNet(neutronV20.UpdateCommand):
    """Update a given provider network."""

    log = logging.getLogger(__name__ + '.UpdateProviderNet')
    resource = 'providernet'
    allow_names = True


class DeleteProviderNet(neutronV20.DeleteCommand):
    """Delete a given provider network."""

    log = logging.getLogger(__name__ + '.DeleteProviderNet')
    resource = 'providernet'
    allow_names = True


class ListProviderNetRange(neutronV20.ListCommand):
    """List provider network segmentation id range."""

    resource = 'providernet_range'
    log = logging.getLogger(__name__ + '.ListProviderNetRange')
    list_columns = ['id', 'name', 'providernet', 'type',
                    'minimum', 'maximum', 'attributes']
    sorting_support = True

    def extend_list(self, data, parsed_args):
        for entry in data:
            # rename attributes
            entry['providernet'] = entry['providernet_name']
            entry['type'] = entry['providernet_type']
            entry['attributes'] = ""
            if 'vxlan' in entry:
                # rename attribute
                entry['attributes'] = _format_vxlan_attributes(entry['vxlan'])
                del entry['vxlan']

    def args2search_opts(self, parsed_args):
        opts = super(ListProviderNetRange, self).args2search_opts(parsed_args)
        opts.update({'sort_key': ['providernet_name', 'minimum'],
                     'sort_dir': ['asc', 'asc']})
        return opts


class ShowProviderNetRange(neutronV20.ShowCommand):
    """Show information for a given provider network segmentation id range."""

    resource = 'providernet_range'
    log = logging.getLogger(__name__ + '.ShowProviderNetRange')
    allow_names = True
    json_indent = 5


def _id_range_value(value):
    range_list = value.split('-')
    if len(range_list) != 2:
        raise argparse.ArgumentTypeError(
            'Expecting MIN_VALUE-MAX_VALUE in range list')
    return {'minimum': range_list[0],
            'maximum': range_list[1]}


class CreateProviderNetRange(neutronV20.CreateCommand):
    """Create a provider network segmentation id range."""

    resource = 'providernet_range'
    log = logging.getLogger(__name__ + '.CreateProviderNetRange')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--shared',
            dest='shared', action='store_true', default=False,
            help=('Set whether a provider network segmentation id range '
                  'may be shared between tenants'))
        parser.add_argument(
            '--description',
            dest='description',
            help='Set user-defined description field for a provider network')
        parser.add_argument(
            '--range', metavar='MIN_VALUE-MAX_VALUE', required=True,
            dest='range', type=_id_range_value,
            help='Segmentation id value range')
        parser.add_argument(
            '--name', required=True,
            dest='name',
            help=('Set user-defined name for a provider network '
                  'segmentation id range'))
        parser.add_argument(
            '--group',
            dest='group',
            help='Multicast IP addresses for VXLAN endpoints')
        parser.add_argument(
            '--ttl', dest='ttl', type=int,
            help='Time-to-live value for VXLAN provider networks')
        parser.add_argument(
            '--port', dest='port', type=int,
            help=('Destination UDP port value to use for '
                  'VXLAN provider networks'))
        parser.add_argument(
            'providernet_id', metavar='PROVIDERNET',
            help='Provider network this segmentation id range belongs to')
        parser.add_argument(
            '--mode',
            dest='mode', default='dynamic',
            choices=['dynamic', 'static', 'evpn'],
            help='Set vxlan learning mode')

    def args2body(self, parsed_args):
        _providernet_id = neutronV20.find_resourceid_by_name_or_id(
            self.get_client(), 'providernet', parsed_args.providernet_id)
        body = {'providernet_range': {
                'providernet_id': _providernet_id,
                'name': parsed_args.name,
                'description': parsed_args.description,
                'shared': parsed_args.shared,
                'minimum': parsed_args.range['minimum'],
                'maximum': parsed_args.range['maximum']}
                }

        if parsed_args.tenant_id:
            body['providernet_range'].update({'tenant_id':
                                              parsed_args.tenant_id})

        if parsed_args.port:
            body['providernet_range'].update({'port': parsed_args.port})

        if parsed_args.ttl:
            body['providernet_range'].update({'ttl': parsed_args.ttl})

        if parsed_args.group:
            body['providernet_range'].update({'group': parsed_args.group})

        if parsed_args.mode:
            body['providernet_range'].update({'mode': parsed_args.mode})

        return body


class UpdateProviderNetRange(neutronV20.UpdateCommand):
    """Update a given provider network segmentation id range."""

    log = logging.getLogger(__name__ + '.UpdateProviderNetRange')
    resource = 'providernet_range'
    allow_names = True

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--description',
            dest='description',
            help='Set user-defined description field for a provider network')
        parser.add_argument(
            '--range', metavar='MIN_VALUE-MAX_VALUE',
            dest='range', type=_id_range_value,
            help='Segmentation id value range')

    def args2body(self, parsed_args):
        body = {'providernet_range': {}}

        if parsed_args.description:
            body['providernet_range'].update(
                {'description': parsed_args.description})

        if parsed_args.range:
            body['providernet_range'].update(
                {'minimum': parsed_args.range['minimum'],
                 'maximum': parsed_args.range['maximum']})

        return body


class DeleteProviderNetRange(neutronV20.DeleteCommand):
    """Delete a given provider network segmentation id range."""

    log = logging.getLogger(__name__ + '.DeleteProviderNetRange')
    resource = 'providernet_range'
    allow_names = True


def _format_segmentation_id(network):
    if network['providernet_type'].lower() == "flat":
        return "n/a"
    return network['segmentation_id']


class ListNetworksOnProviderNet(neutronV20.ListCommand):
    """List the networks on a provider network."""

    log = logging.getLogger(__name__ + '.ListNetworksOnProviderNet')
    list_columns = ['id', 'name', 'vlan_id',
                    'providernet_type', 'segmentation_id',
                    'providernet_attributes']
    _formatters = {'segmentation_id': _format_segmentation_id}
    sorting_support = True
    resource = 'network'
    unknown_parts_flag = False

    def extend_list(self, data, parsed_args):
        for entry in data:
            entry['providernet_attributes'] = ""
            if 'vxlan' in entry:
                # rename attribute
                entry['providernet_attributes'] = (
                    _format_vxlan_attributes(entry['vxlan']))
                del entry['vxlan']

    def get_parser(self, prog_name):
        parser = super(ListNetworksOnProviderNet,
                       self).get_parser(prog_name)
        parser.add_argument(
            'providernet',
            help='Name of the provider network')
        return parser

    def call_server(self, neutron_client, search_opts, parsed_args):
        _id = neutronV20.find_resourceid_by_name_or_id(neutron_client,
                                                       'providernet',
                                                       parsed_args.providernet)
        search_opts['providernet'] = _id
        data = neutron_client.list_networks_on_providernet(
            _id, **search_opts)
        return data


class ListProvidernetConnectivityTests(neutronV20.ListCommand):
    """List provider network connectivity test results."""

    resource = 'providernet_connectivity_test'
    log = logging.getLogger(__name__ + '.ListProviderConnectivityTests')
    list_columns = ['providernet_id', 'providernet_name', 'type', 'host_name',
                    'segmentation_ids', 'status', 'message']
    sorting_support = True

    @staticmethod
    def _list_segments(segments):
        """Takes a list of segments, and outputs them as a string"""
        msg = ", ".join([str(x or "*") for x in sorted(segments)])
        return msg

    def _group_segmentation_id_list(self, segmentation_ids):
        """Takes a list of integers and groups them into ranges"""
        if len(segmentation_ids) < 1:
            return ""
        try:
            sorted_segmentation_ids = sorted(
                [int(segmentation_id) for segmentation_id in segmentation_ids]
            )
        except Exception:
            return self._list_segments(segmentation_ids)
        grouped_ids = [tuple(g[1]) for g in itertools.groupby(
            enumerate(sorted_segmentation_ids), lambda (i, n): i - n
        )]
        msg = ", ".join(
            [(("%s-%s" % (g[0][1], g[-1][1])) if g[0][1] != g[-1][1]
             else ("%s" % g[0][1])) for g in grouped_ids]
        )
        return msg

    def _connectivity_results_to_formatted_dict(self, data):
        """Takes a list of results, and formats them for reporting"""
        parsed_results = {}
        message_key = "hidden"
        for result in data:
            providernet_id = result["providernet_id"]
            providernet_name = result["providernet_name"]
            providernet_type = result["type"]
            hostname = result["host_name"]
            segmentation_id = result.get("segmentation_id", None)
            status = result["status"]
            message = result["message"]
            if message:
                message_key = "message"
            test = (providernet_id, providernet_name, providernet_type,
                    hostname, status, message)
            if test not in parsed_results:
                parsed_results[test] = []
            parsed_results[test].append(segmentation_id)

        formatted_results = []
        for test, results in parsed_results.iteritems():
            (providernet_id, providernet_name, providernet_type,
             hostname, status, message) = test
            formatted_segmentation_ids = \
                self._group_segmentation_id_list(results)
            formatted_result = {"providernet_id": providernet_id,
                                "providernet_name": providernet_name,
                                "type": providernet_type,
                                "host_name": hostname,
                                "status": status,
                                message_key: message,
                                "segmentation_ids": formatted_segmentation_ids}
            formatted_results.append(formatted_result)
        return formatted_results

    def extend_list(self, data, parsed_args):
        formatted_data = self._connectivity_results_to_formatted_dict(data)
        del data[:]
        data.extend(formatted_data)

    def args2search_opts(self, parsed_args):
        opts = super(ListProvidernetConnectivityTests, self).args2search_opts(
            parsed_args
        )
        opts.update({'sort_key': ['status', 'hostname', 'providernet',
                                  'audit_uuid'],
                     'sort_dir': ['asc', 'asc', 'asc', 'asc']})
        return opts


class CreateProvidernetConnectivityTests(neutronV20.CreateCommand):
    """Schedules a providernet connectivity test to be run"""

    resource = 'providernet_connectivity_test'
    log = logging.getLogger(__name__ + '.CreateProvidernetConnectivityTests')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--providernet',
            dest='providernet', default=None,
            help='Schedule audit for given providernet')
        parser.add_argument(
            '--host',
            dest='host', default=None,
            help='Schedule audits for all providernets on host')
        parser.add_argument(
            '--segmentation_id',
            dest='segmentation_id', default=None,
            help='Schedule for this segmentation ID')

    def args2body(self, parsed_args):
        if parsed_args.providernet:
            _providernet_id = neutronV20.find_resourceid_by_name_or_id(
                self.get_client(), 'providernet', parsed_args.providernet
            )
        else:
            _providernet_id = None
        body = {'providernet_connectivity_test': {
                "providernet_id": _providernet_id,
                "host_name": parsed_args.host,
                "segmentation_id": parsed_args.segmentation_id,
                }}
        return body
