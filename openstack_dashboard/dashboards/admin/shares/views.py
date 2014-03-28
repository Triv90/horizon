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
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard.api import manila
from openstack_dashboard.api import keystone

from openstack_dashboard.dashboards.admin.shares \
    import forms as project_forms
from openstack_dashboard.dashboards.admin.shares \
    import tables as project_tables
from openstack_dashboard.dashboards.admin.shares \
    import tabs as project_tabs

from openstack_dashboard.dashboards.project.shares import views


class IndexView(tabs.TabbedTableView, views.ShareTableMixIn):
    tab_group_class = project_tabs.ShareTabs
    template_name = "admin/shares/index.html"


class DetailView(views.DetailView):
    template_name = "admin/shares/detail.html"


class SnapshotDetailView(tabs.TabView):
    tab_group_class = project_tabs.SnapshotDetailTabs
    template_name = 'project/shares/snapshot_detail.html'

    def get_context_data(self, **kwargs):
        context = super(SnapshotDetailView, self).get_context_data(**kwargs)
        context["snapshot"] = self.get_data()
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            snapshot_id = self.kwargs['snapshot_id']
            snapshot = manila.share_snapshot_get(self.request, snapshot_id)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve snapshot details.'),
                              redirect=redirect)
        return snapshot

    def get_tabs(self, request, *args, **kwargs):
        snapshot = self.get_data()
        return self.tab_group_class(request, snapshot=snapshot, **kwargs)
