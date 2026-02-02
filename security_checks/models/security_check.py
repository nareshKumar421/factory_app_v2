# security_checks/models/security_check.py

from django.db import models
from gate_core.models import BaseModel
from driver_management.models import VehicleEntry

class SecurityCheck(BaseModel):

    vehicle_entry = models.OneToOneField(
        VehicleEntry,
        on_delete=models.CASCADE,
        related_name="security_check"
    )

    # Vehicle condition checks
    vehicle_condition_ok = models.BooleanField(default=True)
    tyre_condition_ok = models.BooleanField(default=True)
    fire_extinguisher_available = models.BooleanField(default=True)

    # Seal information
    seal_no_before = models.CharField(max_length=50, blank=True)
    seal_no_after = models.CharField(max_length=50, blank=True)

    # Safety & compliance
    alcohol_test_done = models.BooleanField(default=False)
    alcohol_test_passed = models.BooleanField(default=True)

    # Inspector info
    inspected_by_name = models.CharField(max_length=100)
    inspection_time = models.DateTimeField(auto_now_add=True)

    remarks = models.TextField(blank=True)

    is_submitted = models.BooleanField(default=False)

    def __str__(self):
        return f"Security Check - {self.vehicle_entry.entry_no}"

    def save(self, *args, **kwargs):
        if self.pk:
            old = SecurityCheck.objects.get(pk=self.pk)
            if old.is_submitted:
                raise ValueError("Security check is already submitted and locked.")
        super().save(*args, **kwargs)
