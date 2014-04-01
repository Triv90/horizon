# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
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

from django.core.urlresolvers import NoReverseMatch  # noqa
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title  # noqa
from django.utils import safestring
from django.utils.translation import string_concat, ugettext_lazy  # noqa
from django.utils.translation import ugettext_lazy as _
from django.utils import html

from horizon import exceptions
from horizon import tables

from openstack_dashboard.api import manila
from openstack_dashboard.usage import quotas


DELETABLE_STATES = ("available", "error")


class Create(tables.LinkAction):
    name = "create_share_network"
    verbose_name = _("Create Share Network")
    url = "horizon:project:shares:create_share_network"
    classes = ("ajax-modal", "btn-create")


class Delete(tables.DeleteAction):
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")

    def delete(self, request, obj_id):
        manila.share_network_delete(request, obj_id)

    def allowed(self, request, obj_id):
        sn = manila.share_network_get(request, obj_id)
        return sn.status == "INACTIVE"


class Activate(tables.BatchAction):
    name = "activate"
    action_present = _("Activate")
    action_past = _("Activating")
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")
    verbose_name = _("Activate Share Network")
    #policy_rules = (("share", "volume_extension:types_manage"),)

    def action(self, request, obj_id):
        manila.share_network_activate(request, obj_id)

    def allowed(self, request, share=None):
        usages = quotas.tenant_quota_usages(request)
        if usages['share_networks']['available'] <= 0:
            if "disabled" not in self.classes:
                self.classes = [c for c in self.classes] + ['disabled']
                self.verbose_name = string_concat(self.verbose_name, ' ',
                                                  _("(Quota exceeded)"))
        else:
            self.verbose_name = _("Activate Share Network")
            classes = [c for c in self.classes if c != "disabled"]
            self.classes = classes
        return share.status == "INACTIVE"


class Deactivate(tables.BatchAction):
    name = "deactivate"
    action_present = _("Deactivate")
    action_past = _("Deactivating")
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")
    verbose_name = _("Activate Share Network")

    def action(self, request, obj_id):
        manila.share_network_deactivate(request, obj_id)

    def get_success_url(self, request):
        return reverse('horizon:project:shares:index')

    def allowed(self, request, share=None):
        shares = manila.share_list(request,
                                   search_opts={'share_network_id': share.id})
        if shares:
            return False
        return share.status == "ACTIVE"


class EditShareNetwork(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Share Network")
    url = "horizon:project:shares:update_share_network"
    classes = ("ajax-modal", "btn-create")

    def allowed(self, request, obj_id):
        sn = manila.share_network_get(request, obj_id)
        return sn.status == "INACTIVE"


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, share_net_id):
        share_net = manila.share_network_get(request, share_net_id)
        if not share_net_id.name:
            share_net_id.name = share_net_id
        return share_net


class ShareNetworkTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("INACTIVE", True),
        ("ACTIVATING", None),
        ("DEACTIVATING", None),
        ("ERROR", False),
    )
    name = tables.Column("name", verbose_name=_("Name"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column("network_type",
                                 verbose_name=_("Network Type"))
    neutron_net_id = tables.Column("neutron_net_id",
                                   verbose_name=_("Neutron Net ID"))
    neutron_subnet_id = tables.Column("neutron_subnet_id",
                                   verbose_name=_("Neutron Subnet ID"))
    segmentation_id = tables.Column("segmentation_id",
                                    verbose_name=_("Segmentation Id"))
    status = tables.Column("status", verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    def get_object_display(self, share_network):
        return share_network.name

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta:
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (Create, Delete)
        status_columns = ["status"]
        row_class = UpdateRow
        row_actions = (EditShareNetwork, Delete,
                       Activate, Deactivate)