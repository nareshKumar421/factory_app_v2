import logging
from typing import List

from hdbcli import dbapi

from .connection import HanaConnection
from ..dtos import VendorDTO
from ..exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)


class HanaVendorReader:

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    def get_active_vendors(self) -> List[VendorDTO]:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except dbapi.Error as e:
            logger.error(f"SAP HANA connection failed: {e}")
            raise SAPConnectionError(
                "Unable to connect to SAP HANA. Please try again later."
            ) from e

        try:
            cursor = conn.cursor()
            schema = self.connection.schema

            query = f"""
                SELECT
                    "CardCode"  AS vendor_code,
                    "CardName"  AS vendor_name
                FROM "{schema}"."OCRD"
                WHERE "CardType" = 'S'
                  AND "frozenFor" = 'N'
                ORDER BY "CardName"
            """

            cursor.execute(query)
            rows = cursor.fetchall()

            return [
                VendorDTO(
                    vendor_code=row[0],
                    vendor_name=row[1],
                )
                for row in rows
            ]

        except dbapi.ProgrammingError as e:
            logger.error(f"SAP HANA query error for vendors: {e}")
            raise SAPDataError(
                "Failed to retrieve vendor data from SAP. Invalid query or parameters."
            ) from e
        except dbapi.Error as e:
            logger.error(f"SAP HANA data error for vendors: {e}")
            raise SAPDataError(
                "Failed to retrieve vendor data from SAP. Please try again later."
            ) from e
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception:
                    pass
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
