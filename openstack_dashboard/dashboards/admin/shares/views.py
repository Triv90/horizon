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
