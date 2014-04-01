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
from horizon import tabs

from openstack_dashboard.api import manila

from openstack_dashboard.dashboards.project.shares.share_networks\
    import tables as share_net_tables
from openstack_dashboard.dashboards.project.shares import utils


class ShareNetworkTab(tabs.TableTab):
    table_classes = (share_net_tables.ShareNetworkTable,)
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
        utils.set_tenant_name_to_objects(self.request, share_networks)
        return share_networks
