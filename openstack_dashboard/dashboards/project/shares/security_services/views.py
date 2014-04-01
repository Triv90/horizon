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
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms

from openstack_dashboard.api import manila
from openstack_dashboard.dashboards.project.shares.security_services import\
    forms as sec_services_forms
from openstack_dashboard.dashboards.project.shares.share_networks import forms\
    as share_net_forms


class UpdateView(forms.ModalFormView):
    template_name = "project/shares/share_network_update.html"
    form_class = sec_services_forms.Update
    success_url = 'horizon:project:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)


class CreateView(forms.ModalFormView):
    form_class = sec_services_forms.Create
    template_name = 'project/shares/create_security_service.html'
    success_url = 'horizon:project:shares:index'

    def get_success_url(self):
        return reverse(self.success_url)


class AddSecurityServiceView(forms.ModalFormView):
    form_class = share_net_forms.AddSecurityServiceForm
    template_name = 'project/shares/add_security_service.html'
    success_url = 'horizon:project:shares:index'

    def get_object(self):
        if not hasattr(self, "_object"):
            share_id = self.kwargs['share_network_id']
            try:
                self._object = manila.share_network_get(self.request, share_id)
            except Exception:
                msg = _('Unable to retrieve volume.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(AddSecurityServiceView,
                        self).get_context_data(**kwargs)
        context['share_network'] = self.get_object()
        return context

    def get_initial(self):
        share_net = self.get_object()
        return {'share_net_id': self.kwargs["share_network_id"],
                'name': share_net.name,
                'description': share_net.description}
