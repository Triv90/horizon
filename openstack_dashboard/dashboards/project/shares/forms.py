# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 Nebula, Inc.
# All rights reserved.

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
Views for managing shares.
"""

from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import ValidationError  # noqa
from django.template.defaultfilters import filesizeformat  # noqa
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages
from horizon.utils import fields
from horizon.utils import functions
from horizon.utils.memoized import memoized  # noqa

from openstack_dashboard import api
from openstack_dashboard.api import keystone
from openstack_dashboard.api import manila
from openstack_dashboard.api import neutron
from openstack_dashboard.dashboards.project.images_and_snapshots import utils
from openstack_dashboard.dashboards.project.instances import tables
from openstack_dashboard.usage import quotas


class CreateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
            label=_("Description"), required=False)
    type = forms.ChoiceField(label=_("Type"),
                             required=False)
    size = forms.IntegerField(min_value=1, label=_("Size (GB)"))
    share_network = forms.ChoiceField(label=_("Share Network"),
                                      required=True)
    share_source_type = forms.ChoiceField(label=_("Share Source"),
                                           required=False,
                                           widget=forms.Select(attrs={
                                               'class': 'switchable',
                                               'data-slug': 'source'}))
    snapshot_source = forms.ChoiceField(
        label=_("Use snapshot as a source"),
        widget=fields.SelectWidget(
            attrs={'class': 'snapshot-selector'},
            data_attrs=('size', 'name'),
            transform=lambda x: "%s (%sGB)" % (x.name, x.size)),
        required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateForm, self).__init__(request, *args, **kwargs)
        share_types = ('NFS', 'CIFS')
        share_networks = manila.share_network_list(request)
        self.fields['type'].choices = [(type, type)
                                       for type in share_types]
        self.fields['share_network'].choices = [(net.id, net.id) for net
                                                in share_networks]

        if "snapshot_id" in request.GET:
            try:
                snapshot = self.get_snapshot(request,
                                             request.GET["snapshot_id"])
                self.fields['name'].initial = snapshot.name
                self.fields['size'].initial = snapshot.size
                self.fields['snapshot_source'].choices = ((snapshot.id,
                                                           snapshot),)
                try:
                    # Set the share type from the original share
                    orig_share = manila.share_get(request,
                                                    snapshot.share_id)
                    self.fields['type'].initial = orig_share.share_type
                except Exception:
                    pass
                self.fields['size'].help_text = _('Share size must be equal '
                            'to or greater than the snapshot size (%sGB)') \
                            % snapshot.size
                del self.fields['share_source_type']
            except Exception:
                exceptions.handle(request,
                                  _('Unable to load the specified snapshot.'))
        else:
            source_type_choices = []

            try:
                snapshot_list = manila.share_snapshot_list(request)
                snapshots = [s for s in snapshot_list
                              if s.status == 'available']
                if snapshots:
                    source_type_choices.append(("snapshot_source",
                                                _("Snapshot")))
                    choices = [('', _("Choose a snapshot"))] + \
                              [(s.id, s) for s in snapshots]
                    self.fields['snapshot_source'].choices = choices
                else:
                    del self.fields['snapshot_source']
            except Exception:
                exceptions.handle(request, _("Unable to retrieve "
                        "share snapshots."))

            if source_type_choices:
                choices = ([('no_source_type',
                             _("No source, empty share"))] +
                            source_type_choices)
                self.fields['share_source_type'].choices = choices
            else:
                del self.fields['share_source_type']

    def handle(self, request, data):
        try:
            usages = quotas.tenant_limit_usages(self.request)
            #availableGB = usages['maxTotalShareGigabytes'] - \
            #    usages['gigabytesUsed']
            #availableVol = usages['maxTotalShares'] - usages['sharesUsed']

            snapshot_id = None
            source_type = data.get('share_source_type', None)
            share_network = data.get('share_network', None)
            az = data.get('availability_zone', None) or None
            if (data.get("snapshot_source", None) and
                  source_type in [None, 'snapshot_source']):
                # Create from Snapshot
                snapshot = self.get_snapshot(request,
                                             data["snapshot_source"])
                snapshot_id = snapshot.id
                if (data['size'] < snapshot.size):
                    error_message = _('The share size cannot be less than '
                        'the snapshot size (%sGB)') % snapshot.size
                    raise ValidationError(error_message)
                az = None
            else:
                if type(data['size']) is str:
                    data['size'] = int(data['size'])
            #
            #if availableGB < data['size']:
            #    error_message = _('A share of %(req)iGB cannot be created as '
            #                      'you only have %(avail)iGB of your quota '
            #                      'available.')
            #    params = {'req': data['size'],
            #              'avail': availableGB}
            #    raise ValidationError(error_message % params)
            #elif availableVol <= 0:
            #    error_message = _('You are already using all of your available'
            #                      ' shares.')
            #    raise ValidationError(error_message)

            metadata = {}

            share = manila.share_create(request,
                                        data['size'],
                                        data['name'],
                                        data['description'],
                                        data['type'],
                                        share_network_id=share_network,
                                        snapshot_id=snapshot_id,
                                        metadata=metadata)
            message = _('Creating share "%s"') % data['name']
            messages.info(request, message)
            return share
        except ValidationError as e:
            self.api_error(e.messages[0])
            return False
        except Exception:
            exceptions.handle(request, ignore=True)
            self.api_error(_("Unable to create share."))
            return False

    @memoized
    def get_snapshot(self, request, id):
        return manila.share_snapshot_get(request, id)


class CreateSnapshotForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Snapshot Name"))
    description = forms.CharField(widget=forms.Textarea,
            label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateSnapshotForm, self).__init__(request, *args, **kwargs)

        # populate share_id
        share_id = kwargs.get('initial', {}).get('share_id', [])
        self.fields['share_id'] = forms.CharField(widget=forms.HiddenInput(),
                                                  initial=share_id)

    def handle(self, request, data):
        try:
            share = manila.share_get(request,
                                       data['share_id'])
            force = False
            message = _('Creating share snapshot "%s".') % data['name']
            if share.status == 'in-use':
                force = True
                message = _('Forcing to create snapshot "%s" '
                            'from attached share.') % data['name']
            snapshot = manila.share_snapshot_create(request,
                                                     data['share_id'],
                                                     data['name'],
                                                     data['description'],
                                                     force=force)

            messages.info(request, message)
            return snapshot
        except Exception:
            redirect = reverse("horizon:project:images_and_snapshots:index")
            exceptions.handle(request,
                              _('Unable to create share snapshot.'),
                              redirect=redirect)


class UpdateForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
            label=_("Description"), required=False)

    def handle(self, request, data):
        share_id = self.initial['share_id']
        try:
            manila.share_update(request, share_id, data['name'],
                                 data['description'])

            message = _('Updating share "%s"') % data['name']
            messages.info(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update share.'),
                              redirect=redirect)


class CreateSecurityService(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    dns_ip = forms.CharField(max_length="15", label=_("DNS IP"))
    server = forms.CharField(max_length="255", label=_("Server"))
    domain = forms.CharField(max_length="255", label=_("Domain"))
    sid = forms.CharField(max_length="255", label=_("Sid"))
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(render_value=False))
    confirm_password = forms.CharField(
        label=_("Confirm Password"),
        widget=forms.PasswordInput(render_value=False))
    type = forms.ChoiceField(choices=(("", ""),
                                      ("active_directory", "Active Directory"),
                                      ("ldap", "LDAP"),
                                      ("kerberos", "Kerberos")),
                             label=_("Type"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            security_service = manila.security_service_create(
                request, **data)
            messages.success(request, _('Successfully created security service: %s')
                                      % data['name'])
            return security_service
        except Exception:
            exceptions.handle(request,
                              _('Unable to create security service.'))
            return False


class CreateShareNetworkForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Name"))
    neutron_net_id = forms.ChoiceField(choices=(), label=_("Neutron Net ID"))
    neutron_subnet_id = forms.ChoiceField(choices=(),
                                          label=_("Neutron Subnet ID"))
    #security_service = forms.MultipleChoiceField(
    #    widget=forms.SelectMultiple,
    #    label=_("Security Service"))
    description = forms.CharField(widget=forms.Textarea,
                                  label=_("Description"), required=False)

    def __init__(self, request, *args, **kwargs):
        super(CreateShareNetworkForm, self).__init__(
            request, *args, **kwargs)
        net_choices = neutron.network_list(request)
        subnet_choices = neutron.subnet_list(request)
        sec_services_choices = manila.security_service_list(
            request, search_opts={'all_tenants': True})
        self.fields['neutron_net_id'].choices = [(' ', ' ')] + \
                                                [(choice.id, choice.name_or_id)
                                                 for choice in net_choices]
        self.fields['neutron_subnet_id'].choices = [(' ', ' ')] + \
                                                   [(choice.id,
                                                     choice.name_or_id) for
                                                    choice in subnet_choices]
        #self.fields['security_service'].choices = [(choice.id,
        #                                             choice.name) for
        #                                            choice in
        #                                            sec_services_choices]

    def handle(self, request, data):
        try:
            # Remove any new lines in the public key
            share_network = manila.share_network_create(request, **data)
            messages.success(request, _('Successfully created share network: %s')
                                      % data['name'])
            return share_network
        except Exception:
            exceptions.handle(request,
                              _('Unable to create share network.'))
            return False


class UpdateShareNetworkForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
            label=_("Description"), required=False)

    def handle(self, request, data):
        share_net_id = self.initial['share_network_id']
        try:
            manila.share_network_update(request, share_net_id,
                                        name=data['name'],
                                        description=data['description'])

            message = _('Updating share network "%s"') % data['name']
            messages.info(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update share network.'),
                              redirect=redirect)


class UpdateSecurityServiceForm(forms.SelfHandlingForm):
    name = forms.CharField(max_length="255", label=_("Share Name"))
    description = forms.CharField(widget=forms.Textarea,
            label=_("Description"), required=False)

    def handle(self, request, data):
        sec_service_id = self.initial['security_service_id']
        try:
            manila.security_service_update(request, sec_service_id, data['name'],
                                 data['description'])

            message = _('Updating security service "%s"') % data['name']
            messages.info(request, message)
            return True
        except Exception:
            redirect = reverse("horizon:project:shares:index")
            exceptions.handle(request,
                              _('Unable to update security service.'),
                              redirect=redirect)