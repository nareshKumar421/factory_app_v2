# vehicle_management/models/vehicle_entry.py

# TODO: Not In use

# from django.db import models
# from django.conf import settings
# from gate_core.models import GateEntryBase
# from vehicle_management.models import Vehicle
# from company.models import Company

# class VehicleEntry(GateEntryBase):
#     vehicle = models.ForeignKey(
#         Vehicle,
#         on_delete=models.PROTECT,
#         related_name="vehicle_gate_entries"
#     )

#     created_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="vehicle_vehicleentry_created"
#     )

#     updated_by = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="vehicle_vehicleentry_updated"
#     )

#     entry_time = models.DateTimeField(auto_now_add=True)

#     remarks = models.TextField(blank=True)

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.PROTECT,
#         related_name="vehicle_entries"
#     )

#     def __str__(self):
#         return f"{self.entry_no} - {self.vehicle.vehicle_number}"
