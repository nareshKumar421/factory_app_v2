from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status

from company.models import Company, UserCompany, UserRole
from .serializers import GRPORequestSerializer, GRPOLineRequestSerializer
from .service_layer.grpo_writer import GRPOWriter
from .exceptions import SAPConnectionError, SAPValidationError, SAPDataError

User = get_user_model()


class GRPOSerializerTests(TestCase):
    """Tests for GRPO serializers"""

    def test_grpo_line_serializer_valid(self):
        """Test valid GRPO line data"""
        data = {
            "ItemCode": "ITEM001",
            "Quantity": "100.00",
            "TaxCode": "T1",
            "UnitPrice": "50.00"
        }
        serializer = GRPOLineRequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_grpo_line_serializer_missing_required(self):
        """Test GRPO line with missing required fields"""
        data = {"TaxCode": "T1"}
        serializer = GRPOLineRequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("ItemCode", serializer.errors)
        self.assertIn("Quantity", serializer.errors)

    def test_grpo_request_serializer_valid(self):
        """Test valid GRPO request data"""
        data = {
            "CardCode": "V001",
            "DocumentLines": [
                {
                    "ItemCode": "ITEM001",
                    "Quantity": "100",
                    "TaxCode": "T1",
                    "UnitPrice": "50"
                }
            ]
        }
        serializer = GRPORequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_grpo_request_serializer_missing_card_code(self):
        """Test GRPO request without CardCode"""
        data = {
            "DocumentLines": [
                {"ItemCode": "ITEM001", "Quantity": "100"}
            ]
        }
        serializer = GRPORequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("CardCode", serializer.errors)

    def test_grpo_request_serializer_empty_lines(self):
        """Test GRPO request with empty DocumentLines"""
        data = {
            "CardCode": "V001",
            "DocumentLines": []
        }
        serializer = GRPORequestSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("DocumentLines", serializer.errors)

    def test_grpo_request_serializer_multiple_lines(self):
        """Test GRPO request with multiple lines"""
        data = {
            "CardCode": "V001",
            "DocumentLines": [
                {"ItemCode": "ITEM001", "Quantity": "100", "UnitPrice": "50"},
                {"ItemCode": "ITEM002", "Quantity": "50", "UnitPrice": "75"}
            ]
        }
        serializer = GRPORequestSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(len(serializer.validated_data["DocumentLines"]), 2)


class GRPOWriterTests(TestCase):
    """Tests for GRPOWriter class"""

    def setUp(self):
        self.mock_context = MagicMock()
        self.mock_context.service_layer = {
            "base_url": "https://test-server:50000",
            "company_db": "TEST_DB",
            "username": "test_user",
            "password": "test_pass"
        }
        self.writer = GRPOWriter(self.mock_context)

    @patch("sap_client.service_layer.grpo_writer.ServiceLayerSession")
    @patch("sap_client.service_layer.grpo_writer.requests.post")
    def test_create_grpo_success(self, mock_post, mock_session_class):
        """Test successful GRPO creation"""
        # Mock session login
        mock_session = MagicMock()
        mock_session.login.return_value = {"session_cookie": "abc123"}
        mock_session_class.return_value = mock_session

        # Mock SAP response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "DocEntry": 123,
            "DocNum": 456,
            "CardCode": "V001",
            "CardName": "Test Vendor"
        }
        mock_post.return_value = mock_response

        payload = {
            "CardCode": "V001",
            "DocumentLines": [
                {"ItemCode": "ITEM001", "Quantity": 100}
            ]
        }

        result = self.writer.create(payload)

        self.assertEqual(result["DocEntry"], 123)
        self.assertEqual(result["DocNum"], 456)
        mock_post.assert_called_once()

    @patch("sap_client.service_layer.grpo_writer.ServiceLayerSession")
    @patch("sap_client.service_layer.grpo_writer.requests.post")
    def test_create_grpo_validation_error(self, mock_post, mock_session_class):
        """Test GRPO creation with SAP validation error"""
        mock_session = MagicMock()
        mock_session.login.return_value = {}
        mock_session_class.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": {"value": "Item 'INVALID' does not exist"}
            }
        }
        mock_post.return_value = mock_response

        payload = {"CardCode": "V001", "DocumentLines": [{"ItemCode": "INVALID", "Quantity": 1}]}

        with self.assertRaises(SAPValidationError) as context:
            self.writer.create(payload)

        self.assertIn("does not exist", str(context.exception))

    @patch("sap_client.service_layer.grpo_writer.ServiceLayerSession")
    def test_create_grpo_connection_error(self, mock_session_class):
        """Test GRPO creation with connection error"""
        import requests
        mock_session = MagicMock()
        mock_session.login.side_effect = requests.exceptions.ConnectionError("Connection refused")
        mock_session_class.return_value = mock_session

        payload = {"CardCode": "V001", "DocumentLines": [{"ItemCode": "ITEM001", "Quantity": 1}]}

        with self.assertRaises(SAPConnectionError):
            self.writer.create(payload)


class GRPOAPITests(APITestCase):
    """Integration tests for GRPO API endpoint"""

    def setUp(self):
        self.client = APIClient()

        # Create test user (custom User model uses email as USERNAME_FIELD)
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass123",
            full_name="Test User",
            employee_code="EMP001"
        )

        # Create company and role
        self.company = Company.objects.create(
            name="Test Company",
            code="JIVO_OIL",
            is_active=True
        )
        self.role = UserRole.objects.create(name="Admin")
        self.user_company = UserCompany.objects.create(
            user=self.user,
            company=self.company,
            role=self.role,
            is_default=True,
            is_active=True
        )

        # Authenticate
        self.client.force_authenticate(user=self.user)

    def test_grpo_api_missing_company_header(self):
        """Test GRPO API without Company-Code header"""
        payload = {
            "CardCode": "V001",
            "DocumentLines": [{"ItemCode": "ITEM001", "Quantity": "100"}]
        }
        response = self.client.post("/api/v1/po/grpo/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_grpo_api_invalid_payload(self):
        """Test GRPO API with invalid payload"""
        payload = {"DocumentLines": []}  # Missing CardCode, empty lines

        response = self.client.post(
            "/api/v1/po/grpo/",
            payload,
            format="json",
            HTTP_COMPANY_CODE="JIVO_OIL"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("sap_client.views.SAPClient")
    def test_grpo_api_success(self, mock_client_class):
        """Test successful GRPO creation via API"""
        mock_client = MagicMock()
        mock_client.create_grpo.return_value = {
            "DocEntry": 123,
            "DocNum": 456,
            "CardCode": "V001",
            "CardName": "Test Vendor",
            "DocDate": "2026-02-02",
            "DocTotal": 5000.00
        }
        mock_client_class.return_value = mock_client

        payload = {
            "CardCode": "V001",
            "DocumentLines": [
                {
                    "ItemCode": "ITEM001",
                    "Quantity": "100",
                    "TaxCode": "T1",
                    "UnitPrice": "50"
                }
            ]
        }

        response = self.client.post(
            "/api/v1/po/grpo/",
            payload,
            format="json",
            HTTP_COMPANY_CODE="JIVO_OIL"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["DocNum"], 456)

    @patch("sap_client.views.SAPClient")
    def test_grpo_api_sap_unavailable(self, mock_client_class):
        """Test GRPO API when SAP is unavailable"""
        mock_client = MagicMock()
        mock_client.create_grpo.side_effect = SAPConnectionError("Connection failed")
        mock_client_class.return_value = mock_client

        payload = {
            "CardCode": "V001",
            "DocumentLines": [{"ItemCode": "ITEM001", "Quantity": "100"}]
        }

        response = self.client.post(
            "/api/v1/po/grpo/",
            payload,
            format="json",
            HTTP_COMPANY_CODE="JIVO_OIL"
        )

        self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    @patch("sap_client.views.SAPClient")
    def test_grpo_api_sap_validation_error(self, mock_client_class):
        """Test GRPO API with SAP validation error"""
        mock_client = MagicMock()
        mock_client.create_grpo.side_effect = SAPValidationError("Invalid item code")
        mock_client_class.return_value = mock_client

        payload = {
            "CardCode": "V001",
            "DocumentLines": [{"ItemCode": "INVALID", "Quantity": "100"}]
        }

        response = self.client.post(
            "/api/v1/po/grpo/",
            payload,
            format="json",
            HTTP_COMPANY_CODE="JIVO_OIL"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid item code", response.data["detail"])

    def test_grpo_api_unauthenticated(self):
        """Test GRPO API without authentication"""
        self.client.logout()
        payload = {
            "CardCode": "V001",
            "DocumentLines": [{"ItemCode": "ITEM001", "Quantity": "100"}]
        }

        response = self.client.post(
            "/api/v1/po/grpo/",
            payload,
            format="json",
            HTTP_COMPANY_CODE="JIVO_OIL"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
