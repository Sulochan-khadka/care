from secrets import choice
from uuid import uuid4

from django.urls import reverse

from care.emr.models import Device
from care.emr.resources.device.spec import (
    DeviceAvailabilityStatusChoices,
    DeviceStatusChoices,
)
from care.emr.resources.encounter.constants import (
    ClassChoices,
    EncounterPriorityChoices,
    StatusChoices,
)
from care.emr.tests.test_location_api import FacilityLocationMixin
from care.security.permissions.device import DevicePermissions
from care.security.permissions.encounter import EncounterPermissions
from care.security.permissions.location import FacilityLocationPermissions
from care.utils.tests.base import CareAPITestBase


class DeviceBaseTest(CareAPITestBase, FacilityLocationMixin):
    def setUp(self):
        self.user = self.create_user()
        self.facility = self.create_facility(user=self.user)
        self.facility_organization = self.create_facility_organization(
            facility=self.facility
        )
        self.client.force_authenticate(user=self.user)
        self.patient = self.create_patient()
        self.super_user = self.create_super_user()

    def generate_device_data(self, **kwargs):
        data = {
            "status": choice(list(DeviceStatusChoices)).value,
            "availability_status": choice(list(DeviceAvailabilityStatusChoices)).value,
            "registered_name": self.fake.name(),
        }
        data.update(**kwargs)
        return data

    def create_device(self):
        self.client.force_authenticate(self.super_user)
        url = reverse(
            "device-list", kwargs={"facility_external_id": self.facility.external_id}
        )
        data = self.generate_device_data()
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(self.user)
        return response.json()

    def add_permissions(self, permissions):
        role = self.create_role_with_permissions(permissions)
        self.attach_role_facility_organization_user(
            self.facility_organization, self.user, role
        )

    def get_device_detail_url(self, device):
        return reverse(
            "device-detail",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "external_id": device["id"],
            },
        )

    def get_associate_encounter_url(self, device):
        return reverse(
            "device-associate-encounter",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "external_id": device["id"],
            },
        )

    def get_associate_location_url(self, device):
        return reverse(
            "device-associate-location",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "external_id": device["id"],
            },
        )


class TestDeviceViewSet(DeviceBaseTest):
    def setUp(self):
        super().setUp()
        self.base_url = reverse(
            "device-list", kwargs={"facility_external_id": self.facility.external_id}
        )

    # -------------------- Device CRUD Tests --------------------
    def test_create_device_without_permissions(self):
        data = self.generate_device_data()
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_create_device_with_permissions(self):
        self.add_permissions([DevicePermissions.can_manage_devices.name])
        data = self.generate_device_data()
        response = self.client.post(self.base_url, data=data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_update_device_without_permissions(self):
        device = self.create_device()
        url = self.get_device_detail_url(device)
        data = self.generate_device_data()
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, 403)

    def test_update_device_with_permissions(self):
        device = self.create_device()
        self.add_permissions([DevicePermissions.can_manage_devices.name])
        url = self.get_device_detail_url(device)
        data = self.generate_device_data()
        response = self.client.put(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["registered_name"], data["registered_name"])

    def test_delete_device_without_permissions(self):
        device = self.create_device()
        url = self.get_device_detail_url(device)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_delete_device_with_permissions(self):
        device = self.create_device()
        self.add_permissions([DevicePermissions.can_manage_devices.name])
        url = self.get_device_detail_url(device)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)

    # ------------- Device Encounter Association Tests -------------
    def test_associate_device_encounter_without_device_permission(self):
        device = self.create_device()
        encounter = self.create_encounter(
            self.patient, self.facility, self.facility_organization
        )
        # Only encounter permission attached (missing device permission).
        self.add_permissions([EncounterPermissions.can_write_encounter.name])
        url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter.external_id}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to associate encounter to this device",
        )

    def test_associate_device_encounter_invalid_encounter(self):
        device = self.create_device()
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        url = self.get_associate_encounter_url(device)
        data = {"encounter": str(uuid4())}  # Non-existent encounter ID.
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_associate_device_encounter_different_facility(self):
        device = self.create_device()
        external_facility = self.create_facility(self.user)
        external_org = self.create_facility_organization(external_facility)
        encounter_diff = self.create_encounter(
            self.patient, external_facility, external_org
        )
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter_diff.external_id}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 400)
        error = response.json()["errors"][0]
        self.assertEqual(error["type"], "validation_error")
        self.assertIn("Encounter is not part of given facility", error["msg"])

    def test_associate_device_encounter_success(self):
        device = self.create_device()
        encounter = self.create_encounter(
            self.patient, self.facility, self.facility_organization
        )
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter.external_id}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Device.objects.get(external_id=device["id"]).current_encounter, encounter
        )

    def test_associate_device_encounter_duplicate(self):
        device = self.create_device()
        encounter = self.create_encounter(
            self.patient, self.facility, self.facility_organization
        )
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter.external_id}
        # First association succeeds.
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        # Duplicate association should return a validation error.
        response_dup = self.client.post(url, data=data, format="json")
        self.assertEqual(response_dup.status_code, 400)
        error = response_dup.json()["errors"][0]
        self.assertEqual(error["type"], "validation_error")
        self.assertIn("Encounter already associated", error["msg"])

    def test_disassociate_encounter(self):
        device = self.create_device()
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        url = self.get_associate_encounter_url(device)
        data = {"encounter": None}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            Device.objects.get(external_id=device["id"]).current_encounter
        )

    # ------------- Device Location Association Tests -------------
    def test_associate_device_location_without_permission(self):
        device = self.create_device()
        location = self.create_facility_location()
        self.add_permissions(
            [FacilityLocationPermissions.can_write_facility_locations.name]
        )
        url = self.get_associate_location_url(device)
        data = {"location": location["id"]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["detail"],
            "You do not have permission to associate location to this device",
        )

    def test_associate_device_location_invalid_location(self):
        device = self.create_device()
        self.add_permissions(
            [
                DevicePermissions.can_manage_devices.name,
                FacilityLocationPermissions.can_write_facility_locations.name,
            ]
        )
        url = self.get_associate_location_url(device)
        data = {"location": str(uuid4())}  # Non-existent location.
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 404)

    def test_associate_device_location_success(self):
        device = self.create_device()
        location = self.create_facility_location()
        self.add_permissions(
            [
                DevicePermissions.can_manage_devices.name,
                FacilityLocationPermissions.can_write_facility_locations.name,
            ]
        )
        url = self.get_associate_location_url(device)
        data = {"location": location["id"]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        updated_device = Device.objects.get(external_id=device["id"])
        self.assertEqual(
            str(updated_device.current_location.external_id), location["id"]
        )

    def test_associate_device_location_duplicate(self):
        device = self.create_device()
        location = self.create_facility_location()
        self.add_permissions(
            [
                DevicePermissions.can_manage_devices.name,
                FacilityLocationPermissions.can_write_facility_locations.name,
            ]
        )
        url = self.get_associate_location_url(device)
        data = {"location": location["id"]}
        response_first = self.client.post(url, data=data, format="json")
        self.assertEqual(response_first.status_code, 200)
        response_dup = self.client.post(url, data=data, format="json")
        self.assertEqual(response_dup.status_code, 400)
        error = response_dup.json()["errors"][0]
        self.assertEqual(error["type"], "validation_error")
        self.assertIn("Location already associated", error["msg"])

    def test_disassociate_device_location(self):
        device = self.create_device()
        location = self.create_facility_location()
        self.add_permissions(
            [
                DevicePermissions.can_manage_devices.name,
                FacilityLocationPermissions.can_write_facility_locations.name,
            ]
        )
        url = self.get_associate_location_url(device)
        data = {"location": location["id"]}
        # First associate, then disassociate.
        response_associate = self.client.post(url, data=data, format="json")
        self.assertEqual(response_associate.status_code, 200)
        response_clear = self.client.post(url, data={}, format="json")
        self.assertEqual(response_clear.status_code, 200)
        self.assertIsNone(Device.objects.get(external_id=device["id"]).current_location)

    def test_dissociation_device_encounter_after_encounter_status_update(self):
        device = self.create_device()
        encounter = self.create_encounter(
            self.patient,
            self.facility,
            self.facility_organization,
            status_history={"history": []},
            encounter_class=ClassChoices.imp.value,
        )
        self.add_permissions(
            [
                EncounterPermissions.can_write_encounter.name,
                DevicePermissions.can_manage_devices.name,
            ]
        )
        associate_url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter.external_id}
        response = self.client.post(associate_url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        device_instance = Device.objects.get(external_id=device["id"])
        self.assertEqual(device_instance.current_encounter, encounter)
        self.client.force_authenticate(self.super_user)
        encounter_update_url = reverse(
            "encounter-detail", kwargs={"external_id": encounter.external_id}
        )
        update_data = {
            "status": StatusChoices.completed.value,
            "priority": EncounterPriorityChoices.urgent.value,
            "encounter_class": ClassChoices.imp.value,
        }
        update_response = self.client.put(
            encounter_update_url, data=update_data, format="json"
        )
        self.assertEqual(update_response.status_code, 200)
        device_instance.refresh_from_db()
        self.assertIsNone(device_instance.current_encounter)


class TestDeviceLocationHistoryViewSet(DeviceBaseTest):
    def setUp(self):
        super().setUp()
        self.device = self.create_device()
        self.location = self.create_facility_location()
        self.base_url = reverse(
            "device_location_history-list",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "device_external_id": self.device["id"],
            },
        )

    def associate_location_with_device(self, device, location):
        self.client.force_authenticate(self.super_user)
        url = self.get_associate_location_url(device)
        data = {"location": location["id"]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(self.user)
        return response.json()

    def test_list_device_location_history(self):
        self.associate_location_with_device(self.device, self.location)
        # Without list permission → 403
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 403)
        self.add_permissions([DevicePermissions.can_list_devices.name])
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_retrieve_device_location_history(self):
        history = self.associate_location_with_device(self.device, self.location)
        url = reverse(
            "device_location_history-detail",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "device_external_id": self.device["id"],
                "external_id": history["id"],
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.add_permissions([DevicePermissions.can_list_devices.name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], history["id"])


class TestDeviceEncounterHistoryViewSet(DeviceBaseTest):
    def setUp(self):
        super().setUp()
        self.device = self.create_device()
        self.encounter = self.create_encounter(
            self.patient, self.facility, self.facility_organization
        )
        self.base_url = reverse(
            "device_encounter_history-list",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "device_external_id": self.device["id"],
            },
        )

    def associate_encounter_with_device(self, device, encounter):
        self.client.force_authenticate(self.super_user)
        url = self.get_associate_encounter_url(device)
        data = {"encounter": encounter.external_id}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, 200)
        self.client.force_authenticate(self.user)
        return response.json()

    def test_list_device_encounter_history(self):
        self.associate_encounter_with_device(self.device, self.encounter)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 403)
        self.add_permissions([DevicePermissions.can_list_devices.name])
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_retrieve_device_encounter_history(self):
        history = self.associate_encounter_with_device(self.device, self.encounter)
        url = reverse(
            "device_encounter_history-detail",
            kwargs={
                "facility_external_id": self.facility.external_id,
                "device_external_id": self.device["id"],
                "external_id": history["id"],
            },
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)
        self.add_permissions([DevicePermissions.can_list_devices.name])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], history["id"])
