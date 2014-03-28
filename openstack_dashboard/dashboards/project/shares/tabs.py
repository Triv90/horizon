# Copyright (c) 2014 NetApp, Inc.
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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import messages
from horizon import tabs

from openstack_dashboard.api import keystone
from openstack_dashboard.api import manila

from openstack_dashboard.dashboards.project.\
    shares import tables as project_tables


def set_tenant_name_to_objects(request, objects):
    try:
        tenants, has_more = keystone.tenant_list(request)
    except Exception:
        tenants = []
        msg = _('Unable to retrieve share project information.')
        exceptions.handle(request, msg)

    tenant_dict = dict([(t.id, t) for t in tenants])
    for obj in objects:
        tenant_id = getattr(obj, "project_id", None)
        tenant = tenant_dict.get(tenant_id, None)
        obj.tenant_name = getattr(tenant, "name", None)


class SharesTab(tabs.TableTab):
    table_classes = (project_tables.SharesTable, )
    name = _("Shares")
    slug = "shares_tab"
    template_name = "horizon/common/_detail_table.html"

    def _set_id_if_nameless(self, shares):
        for share in shares:
            # It is possible to create a volume with no name through the
            # EC2 API, use the ID in those cases.
            if not share.name:
                share.name = share.id

    def get_shares_data(self):
        try:
            shares = manila.share_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share list.'))
            return []
        #Gather our tenants to correlate against IDs
        set_tenant_name_to_objects(self.request, shares)
        return shares


class SnapshotsTab(tabs.TableTab):
    table_classes = (project_tables.SnapshotsTable, )
    name = _("Snapshots")
    slug = "snapshots_tab"
    template_name = "horizon/common/_detail_table.html"

    def _set_id_if_nameless(self, snapshots):
        for snap in snapshots:
            if not snap.name:
                snap.name = snap.id

    def get_snapshots_data(self):
        try:
            snapshots = manila.share_snapshot_list(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share list.'))
            return []
        #Gather our tenants to correlate against IDs
        set_tenant_name_to_objects(self.request, snapshots)
        return snapshots


class SecurityServiceTab(tabs.TableTab):
    table_classes = (project_tables.SecurityServiceTable,)
    name = _("Security Services")
    slug = "security_services_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(self.request)
        except Exception:
            security_services = []
            exceptions.handle(self.request,
                              _("Unable to retrieve security services"))

        set_tenant_name_to_objects(self.request, security_services)
        return security_services


class ShareNetworkTab(tabs.TableTab):
    table_classes = (project_tables.ShareNetworkTable,)
    name = _("Share Networks")
    slug = "share_networks_tab"
    template_name = "horizon/common/_detail_table.html"

    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(self.request,
                                                       detailed=True)
        except Exception:
            share_networks = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share networks"))
        set_tenant_name_to_objects(self.request, share_networks)
        return share_networks


class ShareTabs(tabs.TabGroup):
    slug = "share_tabs"
    tabs = (SecurityServiceTab, ShareNetworkTab, SharesTab, SnapshotsTab)
    sticky = True


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"share": self.tab_group.kwargs['share']}


class SnapshotOverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/"
                     "_snapshot_detail_overview.html")

    def get_context_data(self, request):
        return {"snapshot": self.tab_group.kwargs['snapshot']}


class ShareDetailTabs(tabs.TabGroup):
    slug = "share_details"
    tabs = (OverviewTab,)


class SnapshotDetailTabs(tabs.TabGroup):
    slug = "snapshot_details"
    tabs = (SnapshotOverviewTab,)
