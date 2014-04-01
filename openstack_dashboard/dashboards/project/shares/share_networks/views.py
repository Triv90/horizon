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
from horizon import forms
from horizon import workflows
from openstack_dashboard.dashboards.project.shares.share_networks import forms\
    as share_net_forms
from openstack_dashboard.dashboards.project.shares.share_networks \
    import workflows as share_net_workflows


class Update(workflows.WorkflowView):
    workflow_class = share_net_workflows.UpdateShareNetworkWorkflow
    template_name = "project/shares/share_network_update.html"
    success_url = 'horizon:project:shares:index'

    def get_initial(self):
        return {'id': self.kwargs["share_network_id"]}

    def get_context_data(self, **kwargs):
        context = super(Update, self).get_context_data(**kwargs)
        context['id'] = self.kwargs['share_network_id']
        return context


class Create(forms.ModalFormView):
    form_class = share_net_forms.Create
    template_name = 'project/shares/create_share_network.html'
    success_url = 'horizon:project:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)
