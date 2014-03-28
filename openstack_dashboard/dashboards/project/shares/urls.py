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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa

from openstack_dashboard.dashboards.project.shares import views


urlpatterns = patterns('openstack_dashboard.dashboards.project.shares.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^create/$', views.CreateView.as_view(), name='create'),
    url(r'^create_security_service$',
        views.CreateSecurityServiceView.as_view(),
        name='create_security_service'),
    url(r'^create_share_network$',
        views.CreateShareNetworkView.as_view(),
        name='create_share_network'),
    url(r'^share_network/(?P<share_network_id>[^/]+)/update$',
        views.UpdateShareNetworkView.as_view(),
        name='update_share_network'),
    url(r'^/security_service/(?P<sec_service_id>[^/]+)/update/$',
        views.UpdateSecurityServiceView.as_view(),
        name='update_security_service'),
    url(r'^snapshots/(?P<snapshot_id>[^/]+)$',
        views.SnapshotDetailView.as_view(),
        name='snapshot-detail'),
    url(r'^/share-network/(?P<share_network_id>[^/]+)/add_security_service/$',
        views.AddSecurityServiceView.as_view(), name='add_security_service'),
    url(r'^(?P<share_id>[^/]+)/create_snapshot/$',
        views.CreateSnapshotView.as_view(),
        name='create_snapshot'),
    url(r'^(?P<share_id>[^/]+)/$',
        views.DetailView.as_view(),
        name='detail'),
    url(r'^(?P<share_id>[^/]+)/update/$',
        views.UpdateView.as_view(),
        name='update'),

)
