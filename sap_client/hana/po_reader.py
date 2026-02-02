import logging
from typing import List

import pyodbc

from .connection import HanaConnection
from ..dtos import PODTO, POItemDTO
from ..exceptions import SAPConnectionError, SAPDataError

logger = logging.getLogger(__name__)


class HanaPOReader:

    def __init__(self, context):
        self.connection = HanaConnection(context.hana)

    def get_open_pos(self, supplier_code: str) -> List[PODTO]:
        conn = None
        cursor = None

        try:
            conn = self.connection.connect()
        except pyodbc.Error as e:
            logger.error(f"SAP HANA connection failed: {e}")
            raise SAPConnectionError(
                "Unable to connect to SAP HANA. Please try again later."
            ) from e

        try:
            cursor = conn.cursor()
            schema = self.connection.schema

            query = f"""
                SELECT
                    T0."DocNum"        AS po_number,
                    T0."CardCode"      AS supplier_code,
                    T0."CardName"      AS supplier_name,
                    T1."ItemCode"      AS po_item_code,
                    T1."Dscription"    AS item_name,
                    T1."Quantity"      AS ordered_qty,
                    (T1."Quantity" - T1."OpenQty") AS received_qty,
                    T1."OpenQty"       AS remaining_qty,
                    T1."unitMsr"       AS uom
                FROM "{schema}"."OPOR" T0
                JOIN "{schema}"."POR1" T1 ON T0."DocEntry" = T1."DocEntry"
                WHERE T0."CardCode" = ?
                  AND T1."OpenQty" > 0
            """

            cursor.execute(query, supplier_code)
            rows = cursor.fetchall()

            return self._transform_to_dtos(rows)

        except pyodbc.ProgrammingError as e:
            logger.error(f"SAP HANA query error for supplier {supplier_code}: {e}")
            raise SAPDataError(
                "Failed to retrieve PO data from SAP. Invalid query or parameters."
            ) from e
        except pyodbc.Error as e:
            logger.error(f"SAP HANA data error for supplier {supplier_code}: {e}")
            raise SAPDataError(
                "Failed to retrieve PO data from SAP. Please try again later."
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

    def _transform_to_dtos(self, rows) -> List[PODTO]:
        """Group rows by PO and create PODTO objects with nested POItemDTO objects"""
        po_dict = {}

        for row in rows:
            po_number = row[0]
            supplier_code = row[1]
            supplier_name = row[2]

            item = POItemDTO(
                po_item_code=row[3],
                item_name=row[4],
                ordered_qty=float(row[5]),
                received_qty=float(row[6]),
                remaining_qty=float(row[7]),
                uom=row[8]
            )

            if po_number not in po_dict:
                po_dict[po_number] = {
                    'supplier_code': supplier_code,
                    'supplier_name': supplier_name,
                    'items': []
                }

            po_dict[po_number]['items'].append(item)

        po_list = []
        for po_number, po_data in po_dict.items():
            po_list.append(PODTO(
                po_number=str(po_number),
                supplier_code=po_data['supplier_code'],
                supplier_name=po_data['supplier_name'],
                items=po_data['items']
            ))

        return po_list
