# vehicle_management/models/transporter.py

from django.db import models
from gate_core.models import BaseModel

class Transporter(BaseModel):
    name = models.CharField(max_length=150, unique=True)
    contact_person = models.CharField(max_length=100, blank=True)
    mobile_no = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.name

