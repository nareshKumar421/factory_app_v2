# quality_control/models/inspection_parameter_result.py

from django.db import models
from gate_core.models import BaseModel


class InspectionParameterResult(BaseModel):
    """
    Stores the actual test results for each QC parameter.
    """
    inspection = models.ForeignKey(
        "quality_control.RawMaterialInspection",
        on_delete=models.CASCADE,
        related_name="parameter_results"
    )

    # Link to master parameter definition
    parameter_master = models.ForeignKey(
        "quality_control.QCParameterMaster",
        on_delete=models.PROTECT,
        related_name="results"
    )

    # Actual values (copied from master for reference)
    parameter_name = models.CharField(max_length=200)
    standard_value = models.CharField(max_length=200)

    # Test Results
    result_value = models.CharField(max_length=200, blank=True)
    result_numeric = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True
    )

    # Pass/Fail for this parameter
    is_within_spec = models.BooleanField(null=True)

    remarks = models.TextField(blank=True)

    class Meta:
        unique_together = ("inspection", "parameter_master")
        ordering = ["parameter_master__sequence"]

    def __str__(self):
        return f"{self.parameter_name}: {self.result_value}"

    def save(self, *args, **kwargs):
        # Auto-copy parameter name and standard value from master
        if not self.parameter_name and self.parameter_master:
            self.parameter_name = self.parameter_master.parameter_name
        if not self.standard_value and self.parameter_master:
            self.standard_value = self.parameter_master.standard_value

        # Auto-check if within spec for numeric parameters
        if self.result_numeric is not None and self.parameter_master:
            min_val = self.parameter_master.min_value
            max_val = self.parameter_master.max_value
            if min_val is not None and max_val is not None:
                self.is_within_spec = min_val <= self.result_numeric <= max_val

        super().save(*args, **kwargs)
