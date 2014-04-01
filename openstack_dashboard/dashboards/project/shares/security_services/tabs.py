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

from horizon import exceptions, tabs
from horizon import messages
from horizon import tabs

from openstack_dashboard.api import keystone, manila
from openstack_dashboard.api import manila

from openstack_dashboard.dashboards.project.shares.security_services.tables import SecurityServiceTable
from openstack_dashboard.dashboards.project.shares.share_networks.tables import ShareNetworkTable
from openstack_dashboard.dashboards.project.shares.shares.tables import SharesTable
from openstack_dashboard.dashboards.project.shares.snapshots.tables import SnapshotsTable
from openstack_dashboard.dashboards.project.shares.utils import set_tenant_name_to_objects


class SecurityServiceTab(tabs.TableTab):
    table_classes = (SecurityServiceTable,)
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