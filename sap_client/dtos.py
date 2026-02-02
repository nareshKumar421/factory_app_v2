from dataclasses import dataclass
from typing import List


@dataclass
class POItemDTO:
    po_item_code: str
    item_name: str
    ordered_qty: float
    received_qty: float
    remaining_qty: float
    uom: str


@dataclass
class PODTO:
    po_number: str
    supplier_code: str
    supplier_name: str
    items: List[POItemDTO]
