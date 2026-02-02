class SAPValidationError(Exception):
    """Raised when SAP validation fails"""
    pass


class SAPConnectionError(Exception):
    """Raised when SAP connection fails"""
    pass


class SAPDataError(Exception):
    """Raised when SAP data operation fails"""
    pass
