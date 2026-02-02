from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework.exceptions import ValidationError

from driver_management.models import VehicleEntry
from .models import DailyNeedGateEntry
from .serializers import DailyNeedGateEntrySerializer
from .services import complete_daily_need_gate_entry

User = get_user_model()


class DailyNeedGateEntryModelTest(TestCase):
    """Tests for DailyNeedGateEntry model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_str_representation(self):
        """Test string representation of model"""
        # Create a mock vehicle entry first if needed for the test
        # This test assumes vehicle_entry can be mocked or created
        pass

    def test_quantity_must_be_positive(self):
        """Test that quantity validator rejects non-positive values"""
        serializer = DailyNeedGateEntrySerializer(data={
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Test Material",
            "quantity": -1,
            "unit": "KG",
            "receiving_department": "Canteen"
        })
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)


class DailyNeedGateEntrySerializerTest(TestCase):
    """Tests for DailyNeedGateEntrySerializer"""

    def test_valid_data(self):
        """Test serializer with valid data"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Rice",
            "quantity": "10.00",
            "unit": "KG",
            "receiving_department": "Canteen",
            "contact_number": "9876543210"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_invalid_phone_number(self):
        """Test serializer rejects invalid phone number"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Rice",
            "quantity": "10.00",
            "unit": "KG",
            "receiving_department": "Canteen",
            "contact_number": "invalid"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("contact_number", serializer.errors)

    def test_invalid_quantity_zero(self):
        """Test serializer rejects zero quantity"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Rice",
            "quantity": "0",
            "unit": "KG",
            "receiving_department": "Canteen"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)

    def test_invalid_quantity_negative(self):
        """Test serializer rejects negative quantity"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Rice",
            "quantity": "-5",
            "unit": "KG",
            "receiving_department": "Canteen"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("quantity", serializer.errors)

    def test_supplier_name_too_short(self):
        """Test serializer rejects supplier name less than 2 chars"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "A",
            "material_name": "Rice",
            "quantity": "10",
            "unit": "KG",
            "receiving_department": "Canteen"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("supplier_name", serializer.errors)

    def test_valid_phone_with_country_code(self):
        """Test serializer accepts phone with country code"""
        data = {
            "item_category": "CANTEEN",
            "supplier_name": "Test Supplier",
            "material_name": "Rice",
            "quantity": "10.00",
            "unit": "KG",
            "receiving_department": "Canteen",
            "contact_number": "+919876543210"
        }
        serializer = DailyNeedGateEntrySerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)


class DailyNeedGateEntryAPITest(APITestCase):
    """Tests for Daily Need Gate Entry API endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_requires_authentication(self):
        """Test that create endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/v1/daily-needs-gatein/gate-entries/1/daily-need/",
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_requires_authentication(self):
        """Test that complete endpoint requires authentication"""
        self.client.force_authenticate(user=None)
        response = self.client.post(
            "/api/v1/daily-needs-gatein/gate-entries/1/daily-need/complete/",
            {}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_returns_404_for_invalid_entry(self):
        """Test that create returns 404 for non-existent gate entry"""
        response = self.client.post(
            "/api/v1/daily-needs-gatein/gate-entries/99999/daily-need/",
            {
                "item_category": "CANTEEN",
                "supplier_name": "Test",
                "material_name": "Rice",
                "quantity": "10",
                "unit": "KG",
                "receiving_department": "Canteen"
            }
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
