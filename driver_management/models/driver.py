# driver_management/models/driver.py

from django.db import models
from gate_core.models import BaseModel

class Driver(BaseModel):
    name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=15)
    license_no = models.CharField(max_length=50, unique=True)

    id_proof_type = models.CharField(max_length=50, blank=True)
    id_proof_number = models.CharField(max_length=50, blank=True)

    photo = models.ImageField(
        upload_to="drivers/photos/",
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.mobile_no})"
