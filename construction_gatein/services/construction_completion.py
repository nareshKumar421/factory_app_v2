import logging

from django.db import transaction
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

from driver_management.models import VehicleEntry

logger = logging.getLogger(__name__)


@transaction.atomic
def complete_construction_gate_entry(vehicle_entry: VehicleEntry):
    """
    Completes (locks) a Construction / Civil Work Material gate entry.

    Business Rules:
    1. Entry type must be CONSTRUCTION
    2. Security check must be completed and submitted
    3. Construction entry must exist
    4. Security approval must be APPROVED (not PENDING/REJECTED)
    5. Site engineer name is required
    6. Material category must be selected
    7. Contractor name is required

    Args:
        vehicle_entry: VehicleEntry instance to complete

    Raises:
        ValidationError: If any validation check fails
    """

    # Already locked check
    if vehicle_entry.is_locked:
        raise ValidationError("Gate entry already completed")

    # Entry type validation
    if vehicle_entry.entry_type != "CONSTRUCTION":
        raise ValidationError(
            "Invalid entry type for construction completion"
        )

    # Security check must exist
    if not hasattr(vehicle_entry, "security_check"):
        raise ValidationError("Security check not completed")

    # Security check must be submitted
    security_check = vehicle_entry.security_check
    if not getattr(security_check, "is_submitted", False):
        raise ValidationError("Security check not submitted")

    # Construction entry must exist
    if not hasattr(vehicle_entry, "construction_entry"):
        raise ValidationError("Construction entry not filled")

    construction_entry = vehicle_entry.construction_entry

    # Security approval must be APPROVED
    if construction_entry.security_approval != "APPROVED":
        raise ValidationError(
            f"Security approval is {construction_entry.security_approval}. Must be APPROVED to complete."
        )

    # Site engineer is required
    if not construction_entry.site_engineer or not construction_entry.site_engineer.strip():
        raise ValidationError("Site engineer name is required for completion")

    # Material category must be selected
    if not construction_entry.material_category:
        raise ValidationError("Material category must be selected")

    # Contractor name is required
    if not construction_entry.contractor_name or not construction_entry.contractor_name.strip():
        raise ValidationError("Contractor name is required")

    # All validations passed - complete the gate entry
    vehicle_entry.status = "COMPLETED"
    vehicle_entry.is_locked = True
    vehicle_entry.updated_at = now()
    vehicle_entry.save(update_fields=[
        "status",
        "is_locked",
        "updated_at"
    ])

    logger.info(
        f"Construction gate entry completed. Vehicle entry ID: {vehicle_entry.id}"
    )
