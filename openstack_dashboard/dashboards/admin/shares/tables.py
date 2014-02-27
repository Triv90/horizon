# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from openstack_dashboard.api import manila
from openstack_dashboard.dashboards.project.shares \
    import tables as project_tables


class SharesFilterAction(tables.FilterAction):

    def filter(self, table, shares, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [share for share in shares
                if q in share.name.lower()]


class SharesTable(project_tables.SharesTable):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:admin:shares:detail")
    host = tables.Column("os-shr-host-attr:host", verbose_name=_("Host"))
    tenant = tables.Column("tenant_name", verbose_name=_("Project"))

    class Meta:
        name = "shares"
        verbose_name = _("Shares")
        status_columns = ["status"]
        row_class = project_tables.UpdateRow
        table_actions = (project_tables.DeleteShare, SharesFilterAction)
        row_actions = (project_tables.DeleteShare,)
        columns = ('tenant', 'host', 'name', 'size', 'status', 'protocol',)


class CreateSecurityService(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Security Service")
    url = "horizon:admin:shares:create_security_service"
    classes = ("ajax-modal", "btn-create")
    #policy_rules = (("share", "volume_extension:types_manage"),)


class DeleteSecurityService(tables.DeleteAction):
    data_type_singular = _("Security Service")
    data_type_plural = _("Security Services")
    #policy_rules = (("volume", "volume_extension:types_manage"),)

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class CreateShareNetwork(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share Network")
    url = "horizon:admin:shares:create_share_network"
    classes = ("ajax-modal", "btn-create")
    #policy_rules = (("share", "volume_extension:types_manage"),)


class DeleteShareNetwork(tables.DeleteAction):
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")
    #policy_rules = (("volume", "volume_extension:types_manage"),)

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class SecurityServiceTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    tenant = tables.Column("tenant_name", verbose_name=_("Project"))
    dns_ip = tables.Column("dns_ip", verbose_name=_("DNS IP"))
    server = tables.Column("server", verbose_name=_("Server"))
    domain = tables.Column("domain", verbose_name=_("Domain"))
    sid = tables.Column("sid", verbose_name=_("Sid"))

    def get_object_display(self, security_service):
        return security_service.name

    def get_object_id(self, security_service):
        return str(security_service.id)

    class Meta:
        name = "security_services"
        verbose_name = _("Security Services")
        table_actions = (CreateSecurityService, DeleteSecurityService)
        row_actions = (DeleteSecurityService,)


class ShareNetworkTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    tenant = tables.Column("tenant_name", verbose_name=_("Project"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column("network_type",
                                 verbose_name=_("Network Type"))
    neutron_net_id = tables.Column("neutron_net_id",
                                   verbose_name=_("Neutron Net ID"))
    neutron_subnet_id = tables.Column("neutron_subnet_id",
                                   verbose_name=_("Neutron Subnet ID"))
    segmentation_id = tables.Column("segmentation_id",
                                    verbose_name=_("Segmentation Id"))
    status = tables.Column("status", verbose_name=_("Status"))

    def get_object_display(self, share_network):
        return share_network.name

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta:
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (CreateShareNetwork, DeleteShareNetwork)
        row_actions = (DeleteShareNetwork,)