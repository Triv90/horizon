# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
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

from django.core.urlresolvers import reverse
import mock

from openstack_dashboard import api
from openstack_dashboard.dashboards.project.shares import test_data
from openstack_dashboard.test import helpers as test


SHARE_INDEX_URL = reverse('horizon:project:shares:index')


class SnapshotSnapshotViewTests(test.TestCase):

    def test_create_snapshot(self):
        share = test_data.share
        formData = {'name': u'new_snapshot',
                    'description': u'This is test snapshot',
                    'method': u'CreateForm',
                    'size': 1,
                    'type': 'NFS',
                    'share_id': share.id
                    }

        api.manila.share_snapshot_create = mock.Mock()
        api.manila.share_get = mock.Mock(return_value=share)
        url = reverse('horizon:project:shares:create_snapshot',
                      args=[share.id])
        res = self.client.post(url, formData)
        api.manila.share_snapshot_create.assert_called_with(
            mock.ANY, share.id, formData['name'], formData['description'],
            force=False)

    def test_delete_snapshot(self):
        share = test_data.share
        snapshot = test_data.snapshot

        formData = {'action':
                    'snapshots__delete__%s' % snapshot.id}

        api.manila.share_snapshot_delete = mock.Mock()
        api.manila.share_snapshot_get = mock.Mock(
            return_value=snapshot)
        api.manila.share_snapshot_list = mock.Mock(
            return_value=[snapshot])
        api.manila.share_list = mock.Mock(
            return_value=[share])
        url = reverse('horizon:project:shares:index')
        res = self.client.post(url, formData)
        api.manila.share_snapshot_delete.assert_called_with(
            mock.ANY, test_data.snapshot.id)

        self.assertRedirectsNoFollow(res, SHARE_INDEX_URL)

    def test_detail_view(self):
        snapshot = test_data.snapshot
        share = test_data.share
        api.manila.snapshot_get = mock.Mock(return_value=snapshot)
        api.manila.share_get = mock.Mock(return_value=share)

        url = reverse('horizon:project:shares:snapshot-detail',
                      args=[snapshot.id])
        res = self.client.get(url)
        self.assertContains(res, "<h2>Snapshot Details: %s</h2>"
                                 % snapshot.name,
                            1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.name, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.id, 1, 200)
        self.assertContains(res, "<dd>%s</dd>" % snapshot.share_id, 1, 200)
        self.assertContains(res, "<dd>%s GB</dd>" % snapshot.size, 1, 200)

        self.assertNoMessages()

    def test_update_snapshot(self):
        snapshot = test_data.snapshot

        api.manila.share_snapshot_get = mock.Mock(return_value=snapshot)
        api.manila.share_snapshot_update = mock.Mock()

        formData = {'method': 'UpdateForm',
                    'name': snapshot.name,
                    'description': snapshot.description}

        url = reverse('horizon:project:shares:edit_snapshot', args=[snapshot.id])
        res = self.client.post(url, formData)
        self.assertRedirectsNoFollow(
            res, SHARE_INDEX_URL + '?tab=share_tabs__snapshots_tab')
        api.manila.share_snapshot_update.assert_called_once_with(
            mock.ANY, snapshot, display_name=formData['name'],
            display_description=formData['description'])