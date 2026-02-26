# raw_material_gatein/services/validations.py

from decimal import Decimal

OVER_RECEIPT_TOLERANCE = Decimal("1.10")  # 10% tolerance


def validate_received_quantity(ordered_qty, remaining_qty, received_qty):
    if received_qty <= 0:
        raise ValueError("Received quantity must be greater than zero")

    max_allowed = ordered_qty * OVER_RECEIPT_TOLERANCE
    if received_qty > max_allowed:
        raise ValueError(
            f"Received quantity cannot exceed 110% of ordered quantity ({max_allowed})"
        )
