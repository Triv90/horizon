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
Views for managing volumes.
"""

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard.api import manila
from openstack_dashboard.dashboards.project.shares.snapshots import forms \
    as snapshot_forms
from openstack_dashboard.dashboards.project.shares.snapshots.tabs import SnapshotDetailTabs
from openstack_dashboard.usage import quotas


class SnapshotDetailView(tabs.TabView):
    tab_group_class = SnapshotDetailTabs
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


class CreateSnapshotView(forms.ModalFormView):
    form_class = snapshot_forms.CreateSnapshotForm
    template_name = 'project/shares/create_snapshot.html'
    success_url = reverse_lazy("horizon:project:images_and_snapshots:index")

    def get_context_data(self, **kwargs):
        context = super(CreateSnapshotView, self).get_context_data(**kwargs)
        context['share_id'] = self.kwargs['share_id']
        try:
            share = manila.share_get(self.request, context['share_id'])
            if (share.status == 'in-use'):
                context['attached'] = True
                context['form'].set_warning(_("This share is currently "
                                              "attached to an instance. "
                                              "In some cases, creating a "
                                              "snapshot from an attached "
                                              "share can result in a "
                                              "corrupted snapshot."))
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share information.'))
        return context

    def get_initial(self):
        return {'share_id': self.kwargs["share_id"]}