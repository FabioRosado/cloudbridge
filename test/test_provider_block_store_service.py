import uuid

from cloudbridge.providers.interfaces import SnapshotState
from cloudbridge.providers.interfaces import VolumeState
from test.helpers import ProviderTestBase
import test.helpers as helpers


class ProviderBlockStoreServiceTestCase(ProviderTestBase):

    def __init__(self, methodName, provider):
        super(ProviderBlockStoreServiceTestCase, self).__init__(
            methodName=methodName, provider=provider)

    def setUp(self):
        self.instance = helpers.get_test_instance(self.provider)

    def tearDown(self):
        self.instance.terminate()

    def test_crud_volume(self):
        """
        Create a new volume, check whether the expected values are set,
        and delete it
        """
        name = "CBUnitTestCreateVol-{0}".format(uuid.uuid4())
        test_vol = self.provider.block_store.volumes.create_volume(
            name,
            1,
            self.instance.placement_zone)
        with helpers.exception_action(lambda x: test_vol.delete()):
            test_vol.wait_till_ready()
            volumes = self.provider.block_store.volumes.list_volumes()
            found_volumes = [vol for vol in volumes if vol.name == name]
            self.assertTrue(
                len(found_volumes) == 1,
                "List volumes does not return the expected volume %s" %
                name)
            test_vol.delete()
            test_vol.wait_for(
                [VolumeState.DELETED, VolumeState.UNKNOWN],
                terminal_states=[VolumeState.ERROR])
            volumes = self.provider.block_store.volumes.list_volumes()
            found_volumes = [vol for vol in volumes if vol.name == name]
            self.assertTrue(
                len(found_volumes) == 0,
                "Volume %s should have been deleted but still exists." %
                name)

    def test_attach_detach_volume(self):
        """
        Create a new volume, and attempt to attach it to an instance
        """
        name = "CBUnitTestAttachVol-{0}".format(uuid.uuid4())
        test_vol = self.provider.block_store.volumes.create_volume(
            name, 1, self.instance.placement_zone)
        with helpers.exception_action(lambda x: test_vol.delete()):
            test_vol.wait_till_ready()
            test_vol.attach(self.instance, '/dev/sda2')
            test_vol.wait_for(
                [VolumeState.IN_USE], terminal_states=[VolumeState.ERROR,
                                                       VolumeState.DELETED])
            test_vol.detach()
            test_vol.wait_for(
                [VolumeState.AVAILABLE], terminal_states=[VolumeState.ERROR,
                                                          VolumeState.DELETED])
            test_vol.delete()

    def test_crud_snapshot(self):
        """
        Create a new volume, create a snapshot of the volume, and check
        whether list_snapshots properly detects the new snapshot.
        Delete everything afterwards.
        """
        name = "CBUnitTestCreateSnap-{0}".format(uuid.uuid4())
        test_vol = self.provider.block_store.volumes.create_volume(
            name,
            1,
            self.instance.placement_zone)
        with helpers.exception_action(lambda x: test_vol.delete()):
            test_vol.wait_till_ready()
            snap_name = "CBSnapshot-{0}".format(name)
            test_snap = test_vol.create_snapshot(name=snap_name,
                                                 description=snap_name)

            def cleanup_snap(snap):
                snap.delete()
                snap.wait_for(
                    [SnapshotState.UNKNOWN],
                    terminal_states=[SnapshotState.ERROR])

            with helpers.exception_action(lambda x: cleanup_snap(test_snap)):
                test_snap.wait_till_ready()
                snaps = self.provider.block_store.snapshots.list_snapshots()
                found_snaps = [snap for snap in snaps
                               if snap.name == snap_name]
                self.assertTrue(
                    len(found_snaps) == 1,
                    "List snapshots does not return the expected volume %s" %
                    name)
                cleanup_snap(test_snap)
                snaps = self.provider.block_store.snapshots.list_snapshots()
                found_snaps = [snap for snap in snaps
                               if snap.name == snap_name]
                self.assertTrue(
                    len(found_snaps) == 0,
                    "Snapshot %s should have been deleted but still exists." %
                    snap_name)