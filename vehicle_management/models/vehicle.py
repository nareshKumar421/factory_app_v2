# vehicle_management/models/vehicle.py
from django.db import models
from gate_core.models import BaseModel
from .transporter import Transporter



class Vehicle(BaseModel):

    VEHICLE_TYPES = (
        ("TRUCK", "Truck"),
        ("TEMPO", "Tempo"),
        ("CONTAINER", "Container"),
        ("TRACTOR", "Tractor"),
    )

    vehicle_number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    transporter = models.ForeignKey(
        Transporter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    capacity_ton = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.vehicle_number
