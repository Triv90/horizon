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

from django.core.urlresolvers import NoReverseMatch  # noqa
from django.core.urlresolvers import reverse
from django.template.defaultfilters import title  # noqa
from django.utils.translation import string_concat  # noqa
from django.utils.translation import ugettext_lazy as _


from horizon import exceptions
from horizon import tables

from openstack_dashboard.api import manila
from openstack_dashboard.usage import quotas


DELETABLE_STATES = ("available", "error")


class DeleteShare(tables.DeleteAction):
    data_type_singular = _("Share")
    data_type_plural = _("Shares")
    action_past = _("Scheduled deletion of %(data_type)s")
    policy_rules = (("share", "share:delete"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        name = self.table.get_object_display(obj)
        try:
            manila.share_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete share "%s". One or more snapshots '
                    'depend on it.')
            exceptions.check_message(["snapshots", "dependent"], msg % name)
            raise

    def allowed(self, request, share=None):
        if share:
            return share.status in DELETABLE_STATES
        return True


class CreateShare(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Share")
    url = "horizon:project:shares:create"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "share:create"),)

    def allowed(self, request, share=None):
        usages = quotas.tenant_quota_usages(request)
        if usages['shares']['available'] <= 0:
            if "disabled" not in self.classes:
                self.classes = [c for c in self.classes] + ['disabled']
                self.verbose_name = string_concat(self.verbose_name, ' ',
                                                  _("(Quota exceeded)"))
        else:
            self.verbose_name = _("Create Share")
            classes = [c for c in self.classes if c != "disabled"]
            self.classes = classes
        return True


class CreateSnapshot(tables.LinkAction):
    name = "snapshots"
    verbose_name = _("Create Snapshot")
    url = "horizon:project:shares:create_snapshot"
    classes = ("ajax-modal", "btn-camera")
    policy_rules = (("share", "share:create_snapshot"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "project_id", None)
        return {"project_id": project_id}

    def allowed(self, request, share=None):
        return share.status in ("available", "in-use")


class DeleteSnapshot(tables.DeleteAction):
    data_type_singular = _("Snapshot")
    data_type_plural = _("Snapshots")
    action_past = _("Scheduled deletion of %(data_type)s")
    policy_rules = (("snapshot", "snapshot:delete"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "project_id", None)
        return {"project_id": project_id}

    def delete(self, request, obj_id):
        obj = self.table.get_object_by_id(obj_id)
        name = self.table.get_object_display(obj)
        try:
            manila.share_snapshot_delete(request, obj_id)
        except Exception:
            msg = _('Unable to delete snapshot "%s". One or more shares '
                    'depend on it.')
            exceptions.check_message(["snapshots", "dependent"], msg % name)
            raise

    def allowed(self, request, snapshot=None):
        if snapshot:
            return snapshot.status in DELETABLE_STATES
        return True


class EditShare(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Share")
    url = "horizon:project:shares:update"
    classes = ("ajax-modal", "btn-edit")
    policy_rules = (("share", "share:update"),)

    def get_policy_target(self, request, datum=None):
        project_id = None
        if datum:
            project_id = getattr(datum, "os-share-tenant-attr:tenant_id", None)
        return {"project_id": project_id}

    def allowed(self, request, share=None):
        return share.status in ("available", "in-use")


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, share_id):
        share = manila.share_get(request, share_id)
        if not share.name:
            share.name = share_id
        return share


def get_size(share):
    return _("%sGB") % share.size


def get_share_network(share):
    return share.share_network_id if share.share_network_id != "None" else None


class SharesTableBase(tables.DataTable):
    STATUS_CHOICES = (
        ("in-use", True),
        ("available", True),
        ("creating", None),
        ("error", False),
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:shares:detail")
    description = tables.Column("description",
                                verbose_name=_("Description"),
                                truncate=40)
    size = tables.Column(get_size,
                         verbose_name=_("Size"),
                         attrs={'data-type': 'size'})
    status = tables.Column("status",
                           filters=(title,),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    def get_object_display(self, obj):
        return obj.name


class SnapshotsTable(tables.DataTable):
    STATUS_CHOICES = (
        ("in-use", True),
        ("available", True),
        ("creating", None),
        ("error", False),
    )
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:shares:detail")
    description = tables.Column("description",
                                verbose_name=_("Description"),
                                truncate=40)
    size = tables.Column(get_size,
                         verbose_name=_("Size"),
                         attrs={'data-type': 'size'})
    status = tables.Column("status",
                           filters=(title,),
                           verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)
    source = tables.Column("share_id",
                           verbose_name=_("Source"),
                           link="horizon:project:shares:detail")

    def get_object_display(self, obj):
        return obj.name

    class Meta:
        name = "snapshots"
        verbose_name = _("Snapshots")
        status_columns = ["status"]
        row_class = UpdateRow
        table_actions = (DeleteSnapshot, )
        row_actions = (DeleteSnapshot, )


class SharesFilterAction(tables.FilterAction):

    def filter(self, table, shares, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [share for share in shares
                if q in share.name.lower()]


class SharesTable(SharesTableBase):
    name = tables.Column("name",
                         verbose_name=_("Name"),
                         link="horizon:project:shares:detail")
    proto = tables.Column("share_proto",
                          verbose_name=_("Protocol"))
    share_network = tables.Column(get_share_network,
                                  verbose_name=_("Share Network"),
                                  empty_value="-")

    class Meta:
        name = "shares"
        verbose_name = _("Shares")
        status_columns = ["status"]
        row_class = UpdateRow
        table_actions = (CreateShare, DeleteShare, SharesFilterAction)
        row_actions = (EditShare, CreateSnapshot, DeleteShare)


class CreateSecurityService(tables.LinkAction):
    name = "create_security_service"
    verbose_name = _("Create Security Service")
    url = "horizon:project:shares:create_security_service"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "volume_extension:types_manage"),)


class DeleteSecurityService(tables.DeleteAction):
    data_type_singular = _("Security Service")
    data_type_plural = _("Security Services")

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class CreateShareNetwork(tables.LinkAction):
    name = "create_share_network"
    verbose_name = _("Create Share Network")
    url = "horizon:project:shares:create_share_network"
    classes = ("ajax-modal", "btn-create")


class AddSecurityService(tables.LinkAction):
    name = "add_security_service"
    verbose_name = _("Add Security Service")
    url = "horizon:project:shares:add_security_service"
    classes = ("ajax-modal", "btn-create")


class DeleteShareNetwork(tables.DeleteAction):
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")

    def delete(self, request, obj_id):
        manila.share_network_delete(request, obj_id)


class ActivateShareNetwork(tables.BatchAction):
    name = "activate"
    action_present = _("Activate")
    action_past = _("Activating")
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")
    verbose_name = _("Activate Share Network")
    #policy_rules = (("share", "volume_extension:types_manage"),)

    def action(self, request, obj_id):
        manila.share_network_activate(request, obj_id)

    def get_success_url(self, request):
        return reverse('horizon:project:shares:index')

    def allowed(self, request, share=None):
        return share.status == "INACTIVE"


class DeactivateShareNetwork(tables.BatchAction):
    name = "deactivate"
    action_present = _("Deactivate")
    action_past = _("Deactivating")
    data_type_singular = _("Share Network")
    data_type_plural = _("Share Networks")
    verbose_name = _("Activate Share Network")
    #policy_rules = (("share", "volume_extension:types_manage"),)

    def action(self, request, obj_id):
        manila.share_network_deactivate(request, obj_id)

    def get_success_url(self, request):
        return reverse('horizon:project:shares:index')

    def allowed(self, request, share=None):
        return share.status == "ACTIVE"


class EditShareNetwork(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Share Network")
    url = "horizon:project:shares:update_share_network"
    classes = ("ajax-modal", "btn-create")


class EditSecurityService(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit Security Service")
    url = "horizon:project:shares:update_security_service"
    classes = ("ajax-modal", "btn-create")


class SecurityServiceTable(tables.DataTable):
    name = tables.Column("name",
                         verbose_name=_("Name"))
    dns_ip = tables.Column("dns_ip", verbose_name=_("DNS IP"))
    server = tables.Column("server", verbose_name=_("Server"))
    domain = tables.Column("domain", verbose_name=_("Domain"))
    sid = tables.Column("sid", verbose_name=_("Sid"))

    def get_object_display(self, security_service):
        return security_service.name

    def get_object_id(self, security_service):
        return str(security_service.id)

    class Meta:
        name = "security_services"
        verbose_name = _("Security Services")
        table_actions = (CreateSecurityService, DeleteSecurityService)
        row_actions = (EditSecurityService, DeleteSecurityService,)


class ShareNetworkTable(tables.DataTable):
    STATUS_CHOICES = (
        ("ACTIVE", True),
        ("INACTIVE", True),
        ("ACTIVATING", None),
        ("DEACTIVATING", None),
        ("ERROR", False),
    )
    name = tables.Column("name", verbose_name=_("Name"))
    ip_version = tables.Column("ip_version", verbose_name=_("IP Version"))
    network_type = tables.Column("network_type",
                                 verbose_name=_("Network Type"))
    neutron_net_id = tables.Column("neutron_net_id",
                                   verbose_name=_("Neutron Net ID"))
    neutron_subnet_id = tables.Column("neutron_subnet_id",
                                   verbose_name=_("Neutron Subnet ID"))
    segmentation_id = tables.Column("segmentation_id",
                                    verbose_name=_("Segmentation Id"))
    status = tables.Column("status", verbose_name=_("Status"),
                           status=True,
                           status_choices=STATUS_CHOICES)

    def get_object_display(self, share_network):
        return share_network.name

    def get_object_id(self, share_network):
        return str(share_network.id)

    class Meta:
        name = "share_networks"
        verbose_name = _("Share Networks")
        table_actions = (CreateShareNetwork, DeleteShareNetwork)
        status_columns = ["status"]
        row_class = UpdateRow
        row_actions = (EditShareNetwork, DeleteShareNetwork,
                       ActivateShareNetwork, DeactivateShareNetwork,
                       AddSecurityService)