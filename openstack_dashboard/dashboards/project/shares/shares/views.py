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
from openstack_dashboard.dashboards.project.shares.shares import forms \
    as share_form
from openstack_dashboard.dashboards.project.shares.shares.tabs import ShareDetailTabs
from openstack_dashboard.usage import quotas


class ShareTableMixIn(object):
    def _get_shares(self, search_opts=None):
        try:
            return manila.share_list(self.request, search_opts=search_opts)
        except Exception:
            exceptions.handle(self.request,
                              _('Unable to retrieve share list.'))
            return []

    def _set_id_if_nameless(self, shares):
        for share in shares:
            # It is possible to create a volume with no name through the
            # EC2 API, use the ID in those cases.
            if not share.name:
                share.name = share.id


class DetailView(tabs.TabView):
    tab_group_class = ShareDetailTabs
    template_name = 'project/shares/detail.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context["share"] = self.get_data()
        return context

    @memoized.memoized_method
    def get_data(self):
        try:
            share_id = self.kwargs['share_id']
            share = manila.share_get(self.request, share_id)
        except Exception:
            redirect = reverse('horizon:project:shares:index')
            exceptions.handle(self.request,
                              _('Unable to retrieve share details.'),
                              redirect=redirect)
        return share

    def get_tabs(self, request, *args, **kwargs):
        share = self.get_data()
        return self.tab_group_class(request, share=share, **kwargs)


class CreateView(forms.ModalFormView):
    form_class = share_form.CreateForm
    template_name = 'project/shares/create.html'
    success_url = reverse_lazy("horizon:project:shares:index")

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        try:
            context['usages'] = quotas.tenant_limit_usages(self.request)
        except Exception:
            exceptions.handle(self.request)
        return context


class UpdateView(forms.ModalFormView):
    form_class = share_form.UpdateForm
    template_name = 'project/shares/update.html'
    success_url = reverse_lazy("horizon:project:shares:index")

    def get_object(self):
        if not hasattr(self, "_object"):
            vol_id = self.kwargs['share_id']
            try:
                self._object = manila.share_get(self.request, vol_id)
            except Exception:
                msg = _('Unable to retrieve share.')
                url = reverse('horizon:project:shares:index')
                exceptions.handle(self.request, msg, redirect=url)
        return self._object

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['share'] = self.get_object()
        return context

    def get_initial(self):
        share = self.get_object()
        return {'share_id': self.kwargs["share_id"],
                'name': share.name,
                'description': share.description}