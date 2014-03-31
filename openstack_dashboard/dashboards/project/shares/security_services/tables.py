from django.utils.translation import ugettext_lazy as _, ugettext_lazy
from horizon import tables
from openstack_dashboard.api import manila

__author__ = 'yportnova'


class Create(tables.LinkAction):
    name = "create_security_service"
    verbose_name = _("Create Security Service")
    url = "horizon:project:shares:create_security_service"
    classes = ("ajax-modal", "btn-create")
    policy_rules = (("share", "volume_extension:types_manage"),)


class Delete(tables.DeleteAction):
    data_type_singular = _("Security Service")
    data_type_plural = _("Security Services")

    def delete(self, request, obj_id):
        manila.security_service_delete(request, obj_id)


class Edit(tables.LinkAction):
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
        table_actions = (Create, Delete)
        row_actions = (Edit, Delete,)