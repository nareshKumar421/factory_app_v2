from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from gate_core.enums import GateEntryStatus
from company.models import Company
from driver_management.models import VehicleEntry, Driver
from vehicle_management.models import Vehicle
from raw_material_gatein.models import POReceipt, POItemReceipt
from grpo.models import GRPOPosting, GRPOLinePosting, GRPOStatus
from grpo.services import GRPOService

User = get_user_model()


class GRPOModelTests(TestCase):
    """Tests for GRPO models"""

    @classmethod
    def setUpTestData(cls):
        # Create company
        cls.company = Company.objects.create(
            name="Test Company",
            code="TC001"
        )

        # Create user
        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            full_name="Test User",
            employee_code="EMP001"
        )

        # Create vehicle
        cls.vehicle = Vehicle.objects.create(
            vehicle_number="MH12AB1234",
            vehicle_type="TRUCK"
        )

        # Create driver
        cls.driver = Driver.objects.create(
            name="Test Driver",
            mobile_no="9876543210",
            license_no="DL123456"
        )

        # Create vehicle entry
        cls.vehicle_entry = VehicleEntry.objects.create(
            entry_no="VE-2024-001",
            company=cls.company,
            vehicle=cls.vehicle,
            driver=cls.driver,
            entry_type="RAW_MATERIAL",
            status=GateEntryStatus.COMPLETED
        )

        # Create PO receipt
        cls.po_receipt = POReceipt.objects.create(
            vehicle_entry=cls.vehicle_entry,
            po_number="PO-001",
            supplier_code="SUP001",
            supplier_name="Test Supplier"
        )

    def test_grpo_posting_creation(self):
        """Test GRPOPosting model creation"""
        grpo = GRPOPosting.objects.create(
            vehicle_entry=self.vehicle_entry,
            po_receipt=self.po_receipt,
            status=GRPOStatus.PENDING
        )

        self.assertEqual(grpo.status, GRPOStatus.PENDING)
        self.assertIsNone(grpo.sap_doc_entry)
        self.assertIsNone(grpo.sap_doc_num)

    def test_grpo_posting_str(self):
        """Test GRPOPosting string representation"""
        grpo = GRPOPosting.objects.create(
            vehicle_entry=self.vehicle_entry,
            po_receipt=self.po_receipt,
            status=GRPOStatus.POSTED,
            sap_doc_num=12345
        )

        self.assertIn("PO-001", str(grpo))
        self.assertIn("POSTED", str(grpo))

    def test_grpo_unique_constraint(self):
        """Test that same vehicle_entry + po_receipt cannot have duplicate"""
        GRPOPosting.objects.create(
            vehicle_entry=self.vehicle_entry,
            po_receipt=self.po_receipt,
            status=GRPOStatus.PENDING
        )

        with self.assertRaises(Exception):
            GRPOPosting.objects.create(
                vehicle_entry=self.vehicle_entry,
                po_receipt=self.po_receipt,
                status=GRPOStatus.PENDING
            )


class GRPOServiceTests(TestCase):
    """Tests for GRPO service layer"""

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Test Company",
            code="TC001"
        )

        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            full_name="Test User",
            employee_code="EMP001"
        )

        cls.vehicle = Vehicle.objects.create(
            vehicle_number="MH12AB1234",
            vehicle_type="TRUCK"
        )

        cls.driver = Driver.objects.create(
            name="Test Driver",
            mobile_no="9876543210",
            license_no="DL123456"
        )

        cls.vehicle_entry = VehicleEntry.objects.create(
            entry_no="VE-2024-001",
            company=cls.company,
            vehicle=cls.vehicle,
            driver=cls.driver,
            entry_type="RAW_MATERIAL",
            status=GateEntryStatus.COMPLETED
        )

        cls.po_receipt = POReceipt.objects.create(
            vehicle_entry=cls.vehicle_entry,
            po_number="PO-001",
            supplier_code="SUP001",
            supplier_name="Test Supplier"
        )

        cls.po_item = POItemReceipt.objects.create(
            po_receipt=cls.po_receipt,
            po_item_code="ITEM001",
            item_name="Test Item",
            ordered_qty=Decimal("100.000"),
            received_qty=Decimal("100.000"),
            accepted_qty=Decimal("95.000"),
            rejected_qty=Decimal("5.000"),
            uom="KG"
        )

    def test_get_pending_grpo_entries(self):
        """Test fetching pending GRPO entries"""
        service = GRPOService(company_code="TC001")
        entries = service.get_pending_grpo_entries()

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].entry_no, "VE-2024-001")

    def test_get_grpo_preview_data(self):
        """Test getting GRPO preview data"""
        service = GRPOService(company_code="TC001")
        preview_data = service.get_grpo_preview_data(self.vehicle_entry.id)

        self.assertEqual(len(preview_data), 1)
        self.assertEqual(preview_data[0]["po_number"], "PO-001")
        self.assertEqual(preview_data[0]["supplier_code"], "SUP001")
        self.assertTrue(preview_data[0]["is_ready_for_grpo"])
        self.assertEqual(len(preview_data[0]["items"]), 1)

    def test_get_grpo_preview_invalid_entry(self):
        """Test getting preview data for non-existent entry"""
        service = GRPOService(company_code="TC001")

        with self.assertRaises(ValueError) as context:
            service.get_grpo_preview_data(99999)

        self.assertIn("not found", str(context.exception))

    @patch('grpo.services.SAPClient')
    def test_post_grpo_success(self, mock_sap_client):
        """Test successful GRPO posting"""
        # Mock SAP client response
        mock_instance = MagicMock()
        mock_instance.create_grpo.return_value = {
            "DocEntry": 123,
            "DocNum": 456,
            "DocTotal": 4750.00
        }
        mock_sap_client.return_value = mock_instance

        service = GRPOService(company_code="TC001")
        grpo = service.post_grpo(
            vehicle_entry_id=self.vehicle_entry.id,
            po_receipt_id=self.po_receipt.id,
            user=self.user
        )

        self.assertEqual(grpo.status, GRPOStatus.POSTED)
        self.assertEqual(grpo.sap_doc_entry, 123)
        self.assertEqual(grpo.sap_doc_num, 456)

        # Check line posting created
        self.assertEqual(grpo.lines.count(), 1)
        self.assertEqual(grpo.lines.first().quantity_posted, Decimal("95.000"))

    def test_post_grpo_already_posted(self):
        """Test posting GRPO that was already posted"""
        GRPOPosting.objects.create(
            vehicle_entry=self.vehicle_entry,
            po_receipt=self.po_receipt,
            status=GRPOStatus.POSTED,
            sap_doc_num=789
        )

        service = GRPOService(company_code="TC001")

        with self.assertRaises(ValueError) as context:
            service.post_grpo(
                vehicle_entry_id=self.vehicle_entry.id,
                po_receipt_id=self.po_receipt.id,
                user=self.user
            )

        self.assertIn("already posted", str(context.exception))

    def test_post_grpo_entry_not_completed(self):
        """Test posting GRPO for non-completed entry"""
        self.vehicle_entry.status = GateEntryStatus.IN_PROGRESS
        self.vehicle_entry.save()

        service = GRPOService(company_code="TC001")

        with self.assertRaises(ValueError) as context:
            service.post_grpo(
                vehicle_entry_id=self.vehicle_entry.id,
                po_receipt_id=self.po_receipt.id,
                user=self.user
            )

        self.assertIn("not completed", str(context.exception))

        # Reset status
        self.vehicle_entry.status = GateEntryStatus.COMPLETED
        self.vehicle_entry.save()


class GRPOAPITests(APITestCase):
    """Tests for GRPO API endpoints"""

    @classmethod
    def setUpTestData(cls):
        cls.company = Company.objects.create(
            name="Test Company",
            code="TC001"
        )

        cls.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            full_name="Test User",
            employee_code="EMP001"
        )

        cls.vehicle = Vehicle.objects.create(
            vehicle_number="MH12AB1234",
            vehicle_type="TRUCK"
        )

        cls.driver = Driver.objects.create(
            name="Test Driver",
            mobile_no="9876543210",
            license_no="DL123456"
        )

        cls.vehicle_entry = VehicleEntry.objects.create(
            entry_no="VE-2024-001",
            company=cls.company,
            vehicle=cls.vehicle,
            driver=cls.driver,
            entry_type="RAW_MATERIAL",
            status=GateEntryStatus.COMPLETED
        )

        cls.po_receipt = POReceipt.objects.create(
            vehicle_entry=cls.vehicle_entry,
            po_number="PO-001",
            supplier_code="SUP001",
            supplier_name="Test Supplier"
        )

        cls.po_item = POItemReceipt.objects.create(
            po_receipt=cls.po_receipt,
            po_item_code="ITEM001",
            item_name="Test Item",
            ordered_qty=Decimal("100.000"),
            received_qty=Decimal("100.000"),
            accepted_qty=Decimal("95.000"),
            rejected_qty=Decimal("5.000"),
            uom="KG"
        )

    def setUp(self):
        self.client = APIClient()
        # Note: In real tests, you would need to set up proper JWT auth
        # and company context middleware

    def test_pending_grpo_list_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get("/api/v1/grpo/pending/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_grpo_preview_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get(f"/api/v1/grpo/preview/{self.vehicle_entry.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_grpo_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.post("/api/v1/grpo/post/", {
            "vehicle_entry_id": self.vehicle_entry.id,
            "po_receipt_id": self.po_receipt.id
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_grpo_history_unauthenticated(self):
        """Test that unauthenticated requests are rejected"""
        response = self.client.get("/api/v1/grpo/history/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class GRPOSerializerTests(TestCase):
    """Tests for GRPO serializers"""

    def test_grpo_post_request_serializer_valid(self):
        """Test valid GRPO post request serializer"""
        from grpo.serializers import GRPOPostRequestSerializer

        data = {
            "vehicle_entry_id": 1,
            "po_receipt_id": 2,
            "warehouse_code": "WH01",
            "comments": "Test comment"
        }

        serializer = GRPOPostRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_grpo_post_request_serializer_minimal(self):
        """Test minimal GRPO post request"""
        from grpo.serializers import GRPOPostRequestSerializer

        data = {
            "vehicle_entry_id": 1,
            "po_receipt_id": 2
        }

        serializer = GRPOPostRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_grpo_post_request_serializer_invalid(self):
        """Test invalid GRPO post request"""
        from grpo.serializers import GRPOPostRequestSerializer

        data = {
            "vehicle_entry_id": 1
            # Missing required po_receipt_id
        }

        serializer = GRPOPostRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("po_receipt_id", serializer.errors)
