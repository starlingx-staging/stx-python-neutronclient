# Copyright 2012 OpenStack Foundation.
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

import logging

from neutronclient.common import constants
from neutronclient.neutron import v2_0 as neutronV20


class UpdateQoSMixin(object):

    def add_arguments_qos(self, parser):
        parser.add_argument('--name', metavar='NAME',
                            help='Name of QoS policy')
        parser.add_argument('--description', metavar='DESCRIPTION',
                            help="Description of QoS policy", required=False)
        parser.add_argument('--dscp', metavar="POLICY",
                            help='Set of policies for dscp',
                            nargs='+', required=False)
        parser.add_argument('--ratelimit', metavar="POLICY",
                            help='Set of policies for ratelimit',
                            nargs='+', required=False)
        parser.add_argument('--scheduler', metavar="POLICY",
                            help='Set of policies for scheduler',
                            nargs='+', required=False)

    def _args2body_policies(self, qos, type, policies):
            qos['policies'][type] = {}
            for parg in policies:
                args = parg.split('=')
                qos['policies'][type][args[0]] = args[1]

    def args2body_qos(self, parsed_args, qos):
        if parsed_args.name:
            qos['name'] = parsed_args.name

        if parsed_args.description:
            qos['description'] = parsed_args.description

        qos['policies'] = {}
        if parsed_args.dscp:
            self._args2body_policies(qos, constants.TYPE_QOS_DSCP,
                                     parsed_args.dscp)

        if parsed_args.ratelimit:
            self._args2body_policies(qos, constants.TYPE_QOS_RATELIMIT,
                                     parsed_args.ratelimit)

        if parsed_args.scheduler:
            self._args2body_policies(qos, constants.TYPE_QOS_SCHEDULER,
                                     parsed_args.scheduler)


class ListQoS(neutronV20.ListCommand):
    """List QoS policies."""
    resource = 'qos'
    log = logging.getLogger(__name__ + '.ListQoS')

    list_columns = [
        'id', 'name', 'description'
    ]


class ShowQoS(neutronV20.ShowCommand):
    """Show QoS policy."""
    resource = 'qos'
    allow_names = True
    log = logging.getLogger(__name__ + '.ShowQoS')


class DeleteQoS(neutronV20.DeleteCommand):
    """Delete QoS policy."""
    resource = 'qos'
    allow_names = True
    log = logging.getLogger(__name__ + '.DeleteQoS')


class UpdateQoS(neutronV20.UpdateCommand, UpdateQoSMixin):
    """Update QoS policy."""
    resource = 'qos'
    log = logging.getLogger(__name__ + '.UpdateQoS')

    def add_known_arguments(self, parser):
        self.add_arguments_qos(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}}
        self.args2body_qos(parsed_args, body[self.resource])
        return body


class CreateQoS(neutronV20.CreateCommand, UpdateQoSMixin):
    """Create QoS policy."""
    resource = 'qos'
    log = logging.getLogger(__name__ + '.CreateQoS')

    def add_known_arguments(self, parser):
        self.add_arguments_qos(parser)

    def args2body(self, parsed_args):
        body = {self.resource: {}}

        if parsed_args.tenant_id:
            body[self.resource]['tenant_id'] = parsed_args.tenant_id

        self.args2body_qos(parsed_args, body[self.resource])
        return body
