# quality_control/models/material_type.py

from django.db import models
from gate_core.models import BaseModel
from company.models import Company


class MaterialType(BaseModel):
    """
    Master table for material types/categories.
    Each material type can have different QC parameters.
    """
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="material_types"
    )

    class Meta:
        unique_together = ("code", "company")
        ordering = ["name"]
        permissions = [
            ("can_manage_material_types", "Can manage material types"),
            ("can_manage_qc_parameters", "Can manage QC parameters"),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"
