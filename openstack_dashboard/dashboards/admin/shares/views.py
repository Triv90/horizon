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

"""
Admin views for managing shares.
"""

from django.core.urlresolvers import reverse
from django.utils.datastructures import SortedDict
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tables

from openstack_dashboard.api import manila
from openstack_dashboard.api import keystone

from openstack_dashboard.dashboards.admin.shares \
    import forms as project_forms
from openstack_dashboard.dashboards.admin.shares \
    import tables as project_tables

from openstack_dashboard.dashboards.project.shares import views


class IndexView(tables.MultiTableView, views.ShareTableMixIn):
    table_classes = (project_tables.SharesTable,
                     project_tables.ShareNetworkTable,
                     project_tables.SecurityServiceTable)
    template_name = "admin/shares/index.html"

    def get_shares_data(self):
        shares = self._get_shares(search_opts={'all_tenants': True})
        self._set_id_if_nameless(shares)

        # Gather our tenants to correlate against IDs
        try:
            tenants, has_more = keystone.tenant_list(self.request)
        except Exception:
            tenants = []
            msg = _('Unable to retrieve share project information.')
            exceptions.handle(self.request, msg)

        tenant_dict = SortedDict([(t.id, t) for t in tenants])
        for share in shares:
            tenant_id = getattr(share, "tenant_id", None)
            tenant = tenant_dict.get(tenant_id, None)
            share.tenant_name = getattr(tenant, "name", None)

        return shares

    def get_security_services_data(self):
        try:
            security_services = manila.security_service_list(
                self.request, search_opts={'all_tenants': True})
        except Exception:
            security_services = []
            exceptions.handle(self.request,
                              _("Unable to retrieve security services"))
        return security_services

    def get_share_networks_data(self):
        try:
            share_networks = manila.share_network_list(
                self.request, search_opts={'all_tenants': True})
        except Exception:
            share_networks = []
            exceptions.handle(self.request,
                              _("Unable to retrieve share networks"))
        return share_networks


class DetailView(views.DetailView):
    template_name = "admin/shares/detail.html"


class CreateSecurityServiceView(forms.ModalFormView):
    form_class = project_forms.CreateSecurityService
    template_name = 'admin/shares/create_security_service.html'
    success_url = 'horizon:admin:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)


class CreateShareNetworkView(forms.ModalFormView):
    form_class = project_forms.CreateShareNetwork
    template_name = 'admin/shares/create_share_network.html'
    success_url = 'horizon:admin:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)