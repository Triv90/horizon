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

from openstack_dashboard.dashboards.project.shares.shares \
    import tables as share_tables
from openstack_dashboard.dashboards.project.shares import utils


class SharesTab(tabs.TableTab):
    table_classes = (share_tables.SharesTable, )
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
        utils.set_tenant_name_to_objects(self.request, shares)
        return shares


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("project/shares/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"share": self.tab_group.kwargs['share']}


class ShareDetailTabs(tabs.TabGroup):
    slug = "share_details"
    tabs = (OverviewTab,)
