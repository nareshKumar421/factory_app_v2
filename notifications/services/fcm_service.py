import logging

from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy import firebase_admin to allow migrations to run without it installed
firebase_admin = None
credentials = None
messaging = None


def _import_firebase():
    global firebase_admin, credentials, messaging
    if firebase_admin is None:
        try:
            import firebase_admin as _firebase_admin
            from firebase_admin import credentials as _credentials
            from firebase_admin import messaging as _messaging
            firebase_admin = _firebase_admin
            credentials = _credentials
            messaging = _messaging
        except ImportError:
            raise ImportError(
                "firebase-admin package is required. Install it with: pip install firebase-admin"
            )


class FCMService:
    """
    Low-level Firebase Cloud Messaging service.
    Handles FCM SDK initialization and message sending.
    """

    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK (singleton pattern)."""
        if cls._initialized:
            return

        _import_firebase()

        try:
            cred = credentials.Certificate(settings.FCM_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)
            cls._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase Admin SDK: {e}")
            raise

    @classmethod
    def send_to_token(cls, token: str, title: str, body: str, data: dict = None) -> dict:
        """
        Send notification to a single device token.

        Returns:
            dict with 'success', 'message_id', and 'error' keys
        """
        _import_firebase()
        cls.initialize()

        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            token=token,
        )

        try:
            response = messaging.send(message)
            logger.info(f"FCM message sent successfully: {response}")
            return {
                "success": True,
                "message_id": response,
                "error": None
            }
        except messaging.UnregisteredError:
            logger.warning(f"FCM token unregistered: {token[:20]}...")
            return {
                "success": False,
                "message_id": None,
                "error": "TOKEN_UNREGISTERED"
            }
        except Exception as e:
            logger.error(f"FCM send failed: {e}")
            return {
                "success": False,
                "message_id": None,
                "error": str(e)
            }

    @classmethod
    def send_to_multiple(cls, tokens: list, title: str, body: str, data: dict = None) -> dict:
        """
        Send notification to multiple device tokens.

        Returns:
            dict with 'success_count', 'failure_count', and 'responses' keys
        """
        if not tokens:
            return {
                "success_count": 0,
                "failure_count": 0,
                "responses": []
            }

        _import_firebase()
        cls.initialize()

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data or {},
            tokens=tokens,
        )

        try:
            response = messaging.send_each_for_multicast(message)

            results = []
            for idx, send_response in enumerate(response.responses):
                if send_response.success:
                    results.append({
                        "token": tokens[idx],
                        "success": True,
                        "message_id": send_response.message_id
                    })
                else:
                    results.append({
                        "token": tokens[idx],
                        "success": False,
                        "error": str(send_response.exception)
                    })

            return {
                "success_count": response.success_count,
                "failure_count": response.failure_count,
                "responses": results
            }
        except Exception as e:
            logger.error(f"FCM multicast send failed: {e}")
            return {
                "success_count": 0,
                "failure_count": len(tokens),
                "responses": [],
                "error": str(e)
            }
