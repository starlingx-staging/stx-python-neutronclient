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

from __future__ import print_function

import argparse
import logging

from cliff import lister
from cliff import show

from neutronclient._i18n import _
from neutronclient.common import exceptions
from neutronclient.common import utils
from neutronclient.neutron import v2_0 as neutronV20

LOG = logging.getLogger(__name__)


def get_tenant_id(tenant_id, client):
    return (tenant_id if tenant_id else
            client.get_settings_tenant()['tenant']['tenant_id'])


class DeleteSetting(neutronV20.NeutronCommand):
    """Delete defined settings of a given tenant."""

    resource = 'setting'
    log = logging.getLogger(__name__ + '.DeleteSetting')

    def get_parser(self, prog_name):
        parser = super(DeleteSetting, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        obj_deleter = getattr(neutron_client,
                              "delete_%s" % self.resource)
        obj_deleter(tenant_id)
        print((_('Deleted %(resource)s: %(tenant_id)s')
               % {'tenant_id': tenant_id,
                  'resource': self.resource}),
              file=self.app.stdout)
        return


class ListSetting(neutronV20.NeutronCommand, lister.Lister):
    """List settings of all tenants who have non-default setting values."""

    resource = 'setting'
    log = logging.getLogger(__name__ + '.ListSetting')

    def get_parser(self, prog_name):
        parser = super(ListSetting, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('get_data(%s)', parsed_args)
        neutron_client = self.get_client()
        search_opts = {}
        self.log.debug('search options: %s', search_opts)
        neutron_client.format = parsed_args.request_format
        obj_lister = getattr(neutron_client,
                             "list_%ss" % self.resource)
        data = obj_lister(**search_opts)
        info = []
        collection = self.resource + "s"
        if collection in data:
            info = data[collection]
        _columns = len(info) > 0 and sorted(info[0].keys()) or []
        return (_columns, (utils.get_item_properties(s, _columns)
                for s in info))


class ShowSetting(neutronV20.NeutronCommand, show.ShowOne):
    """Show settings of a given tenant

    """
    resource = "setting"
    log = logging.getLogger(__name__ + '.ShowSetting')

    def get_parser(self, prog_name):
        parser = super(ShowSetting, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('get_data(%s)', parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        params = {}
        obj_shower = getattr(neutron_client,
                             "show_%s" % self.resource)
        data = obj_shower(tenant_id, **params)
        if self.resource in data:
            for k, v in data[self.resource].iteritems():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += utils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].iteritems()))
        else:
            return None


class UpdateSetting(neutronV20.NeutronCommand, show.ShowOne):
    """Define tenant's setting not to use defaults."""

    resource = 'setting'
    log = logging.getLogger(__name__ + '.UpdateSetting')

    def get_parser(self, prog_name):
        parser = super(UpdateSetting, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant-id', metavar='tenant-id',
            help=_('The owner tenant ID'))
        parser.add_argument(
            '--tenant_id',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--mac-filtering', metavar='mac_filtering',
            help=_('Enable/Disable source MAC filtering on all ports'))
        return parser

    def _validate_boolean(self, name, value):
        try:
            return_value = bool(value.lower() in ['yes', 'true', 'enabled'])
        except Exception:
            message = (_('Setting value for %(name)s must be a boolean') %
                       {'name': name})
            raise exceptions.NeutronClientException(message=message)
        return return_value

    def args2body(self, parsed_args):
        settings = {}
        for name in ['mac_filtering']:
            if getattr(parsed_args, name):
                settings[name] = self._validate_boolean(
                    name,
                    getattr(parsed_args, name))
        if (len(settings) == 0):
            message = (_('No recognized settings'))
            raise exceptions.NeutronClientException(message=message)
        return {self.resource: settings}

    def take_action(self, parsed_args):
        self.log.debug('run(%s)', parsed_args)
        neutron_client = self.get_client()
        neutron_client.format = parsed_args.request_format
        _extra_values = neutronV20.parse_args_to_dict(self.values_specs)
        neutronV20._merge_args(self, parsed_args, _extra_values,
                               self.values_specs)
        body = self.args2body(parsed_args)
        if self.resource in body:
            body[self.resource].update(_extra_values)
        else:
            body[self.resource] = _extra_values
        obj_updator = getattr(neutron_client,
                              "update_%s" % self.resource)
        tenant_id = get_tenant_id(parsed_args.tenant_id,
                                  neutron_client)
        data = obj_updator(tenant_id, body)
        if self.resource in data:
            for k, v in data[self.resource].iteritems():
                if isinstance(v, list):
                    value = ""
                    for _item in v:
                        if value:
                            value += "\n"
                        if isinstance(_item, dict):
                            value += utils.dumps(_item)
                        else:
                            value += str(_item)
                    data[self.resource][k] = value
                elif v is None:
                    data[self.resource][k] = ''
            return zip(*sorted(data[self.resource].iteritems()))
        else:
            return None
