# raw_material_gatein/services/validations.py

def validate_received_quantity(ordered_qty, remaining_qty, received_qty):
    if received_qty <= 0:
        raise ValueError("Received quantity must be greater than zero")

    if received_qty > remaining_qty:
        raise ValueError("Received quantity cannot exceed remaining PO quantity")
